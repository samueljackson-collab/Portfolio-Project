// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "@chainlink/contracts/src/v0.8/ChainlinkClient.sol";

contract PortfolioOracleConsumer is ChainlinkClient {
    using Chainlink for Chainlink.Request;

    uint256 public latestMetric;
    bytes32 private jobId;
    uint256 private fee;

    constructor(address token, address oracle, bytes32 _jobId, uint256 _fee) {
        setChainlinkToken(token);
        setChainlinkOracle(oracle);
        jobId = _jobId;
        fee = _fee;
    }

    function requestMetric() public returns (bytes32 requestId) {
        Chainlink.Request memory request = buildChainlinkRequest(jobId, address(this), this.fulfill.selector);
        request.add("metric", "portfolio_health_score");
        return sendChainlinkRequest(request, fee);
    }

    function fulfill(bytes32 _requestId, uint256 metric) public recordChainlinkFulfillment(_requestId) {
        latestMetric = metric;
    }
}
