// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "@chainlink/contracts/src/v0.8/ChainlinkClient.sol";
import "@chainlink/contracts/src/v0.8/shared/access/ConfirmedOwner.sol";
import "@openzeppelin/contracts/utils/cryptography/ECDSA.sol";

/**
 * @title PortfolioOracleConsumer
 * @notice Enhanced Chainlink oracle consumer with signature verification
 * @dev Supports multiple oracle requests and response verification
 */
contract PortfolioOracleConsumer is ChainlinkClient, ConfirmedOwner {
    using Chainlink for Chainlink.Request;
    using ECDSA for bytes32;

    // Oracle configuration
    address public oracleSigner;
    bytes32 public jobId;
    uint256 public fee;

    // Request tracking
    struct OracleRequest {
        address requester;
        string metricType;
        uint256 timestamp;
        bool fulfilled;
        uint256 value;
        bytes signature;
    }

    mapping(bytes32 => OracleRequest) public requests;
    mapping(string => uint256) public latestValues;
    mapping(string => uint256) public lastUpdated;

    // Legacy compatibility
    uint256 public latestMetric;

    // Events
    event MetricRequested(
        bytes32 indexed requestId,
        address indexed requester,
        string metricType
    );

    event MetricFulfilled(
        bytes32 indexed requestId,
        string metricType,
        uint256 value,
        uint256 timestamp
    );

    event OracleSignerUpdated(address indexed oldSigner, address indexed newSigner);
    event SignatureVerified(bytes32 indexed requestId, bool valid);

    // Errors
    error InvalidSignature();
    error RequestAlreadyFulfilled();
    error StaleData();

    /**
     * @notice Initialize the oracle consumer
     * @param _link LINK token address
     * @param _oracle Chainlink oracle address
     * @param _jobId Job ID for the oracle
     * @param _fee Fee in LINK for requests
     */
    constructor(
        address _link,
        address _oracle,
        bytes32 _jobId,
        uint256 _fee
    ) ConfirmedOwner(msg.sender) {
        setChainlinkToken(_link);
        setChainlinkOracle(_oracle);
        jobId = _jobId;
        fee = _fee;
    }

    /**
     * @notice Request a portfolio metric from the oracle
     * @return requestId The Chainlink request ID
     */
    function requestMetric() public returns (bytes32 requestId) {
        return requestMetricByType("portfolio_health_score");
    }

    /**
     * @notice Request a specific metric type from the oracle
     * @param metricType Type of metric to request
     * @return requestId The Chainlink request ID
     */
    function requestMetricByType(string memory metricType) public returns (bytes32 requestId) {
        Chainlink.Request memory req = buildChainlinkRequest(
            jobId,
            address(this),
            this.fulfill.selector
        );

        req.add("metric", metricType);
        req.add("get", "data.result");
        req.addInt("times", 1);

        requestId = sendChainlinkRequest(req, fee);

        requests[requestId] = OracleRequest({
            requester: msg.sender,
            metricType: metricType,
            timestamp: block.timestamp,
            fulfilled: false,
            value: 0,
            signature: ""
        });

        emit MetricRequested(requestId, msg.sender, metricType);
    }

    /**
     * @notice Fulfill an oracle request (called by Chainlink)
     * @param _requestId The request ID
     * @param metric The metric value
     */
    function fulfill(
        bytes32 _requestId,
        uint256 metric
    ) external recordChainlinkFulfillment(_requestId) {
        OracleRequest storage request = requests[_requestId];

        if (request.fulfilled) {
            revert RequestAlreadyFulfilled();
        }

        request.fulfilled = true;
        request.value = metric;

        // Update latest values
        latestMetric = metric;
        latestValues[request.metricType] = metric;
        lastUpdated[request.metricType] = block.timestamp;

        emit MetricFulfilled(_requestId, request.metricType, metric, block.timestamp);
    }

    /**
     * @notice Fulfill with signature verification for enhanced security
     * @param requestId The request ID
     * @param value The metric value
     * @param timestamp Oracle timestamp
     * @param signature ECDSA signature from oracle
     */
    function fulfillWithSignature(
        bytes32 requestId,
        uint256 value,
        uint256 timestamp,
        bytes calldata signature
    ) external {
        OracleRequest storage request = requests[requestId];

        if (request.fulfilled) {
            revert RequestAlreadyFulfilled();
        }

        // Verify signature if signer is set
        if (oracleSigner != address(0)) {
            bytes32 messageHash = keccak256(abi.encodePacked(requestId, value, timestamp));
            bytes32 ethSignedHash = messageHash.toEthSignedMessageHash();
            address signer = ethSignedHash.recover(signature);

            if (signer != oracleSigner) {
                revert InvalidSignature();
            }

            // Check for stale data (5 minute tolerance)
            if (block.timestamp > timestamp + 300) {
                revert StaleData();
            }

            emit SignatureVerified(requestId, true);
        }

        request.fulfilled = true;
        request.value = value;
        request.signature = signature;

        latestMetric = value;
        latestValues[request.metricType] = value;
        lastUpdated[request.metricType] = block.timestamp;

        emit MetricFulfilled(requestId, request.metricType, value, timestamp);
    }

    /**
     * @notice Get the latest value for a metric
     * @param metricType The metric type
     * @return value The latest value
     * @return timestamp When it was last updated
     */
    function getLatestMetric(string calldata metricType)
        external
        view
        returns (uint256 value, uint256 timestamp)
    {
        return (latestValues[metricType], lastUpdated[metricType]);
    }

    /**
     * @notice Get request details
     * @param requestId The request ID
     */
    function getRequest(bytes32 requestId)
        external
        view
        returns (
            address requester,
            string memory metricType,
            uint256 timestamp,
            bool fulfilled,
            uint256 value
        )
    {
        OracleRequest storage req = requests[requestId];
        return (req.requester, req.metricType, req.timestamp, req.fulfilled, req.value);
    }

    /**
     * @notice Update the oracle signer address
     * @param newSigner New signer address
     */
    function setOracleSigner(address newSigner) external onlyOwner {
        emit OracleSignerUpdated(oracleSigner, newSigner);
        oracleSigner = newSigner;
    }

    /**
     * @notice Update oracle configuration
     * @param _oracle New oracle address
     * @param _jobId New job ID
     * @param _fee New fee amount
     */
    function setOracleConfig(
        address _oracle,
        bytes32 _jobId,
        uint256 _fee
    ) external onlyOwner {
        setChainlinkOracle(_oracle);
        jobId = _jobId;
        fee = _fee;
    }

    /**
     * @notice Withdraw LINK tokens
     */
    function withdrawLink() external onlyOwner {
        LinkTokenInterface link = LinkTokenInterface(chainlinkTokenAddress());
        require(link.transfer(msg.sender, link.balanceOf(address(this))), "Transfer failed");
    }
}
