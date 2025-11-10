// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "@openzeppelin/contracts/token/ERC20/IERC20.sol";
import "@openzeppelin/contracts/access/Ownable.sol";

/// @title PortfolioStaking
/// @notice Users stake governance tokens and earn rewards based on holding duration.
contract PortfolioStaking is Ownable {
    IERC20 public immutable stakingToken;
    IERC20 public immutable rewardToken;

    struct StakeInfo {
        uint256 balance;
        uint256 rewardDebt;
        uint256 lastUpdated;
    }

    mapping(address => StakeInfo) private stakes;
    uint256 public accRewardPerToken;
    uint256 public totalStaked;
    uint256 public rewardRatePerSecond;

    event Staked(address indexed user, uint256 amount);
    event Withdrawn(address indexed user, uint256 amount);
    event RewardClaimed(address indexed user, uint256 amount);

    constructor(IERC20 _stakingToken, IERC20 _rewardToken) {
        stakingToken = _stakingToken;
        rewardToken = _rewardToken;
    }

    function setRewardRate(uint256 newRate) external onlyOwner {
        _updateRewards(address(0));
        rewardRatePerSecond = newRate;
    }

    function stake(uint256 amount) external {
        require(amount > 0, "amount = 0");
        _updateRewards(msg.sender);
        stakingToken.transferFrom(msg.sender, address(this), amount);
        stakes[msg.sender].balance += amount;
        totalStaked += amount;
        emit Staked(msg.sender, amount);
    }

    function withdraw(uint256 amount) external {
        StakeInfo storage info = stakes[msg.sender];
        require(info.balance >= amount, "insufficient");
        _updateRewards(msg.sender);
        info.balance -= amount;
        totalStaked -= amount;
        stakingToken.transfer(msg.sender, amount);
        emit Withdrawn(msg.sender, amount);
    }

    function claim() external {
        _updateRewards(msg.sender);
        uint256 pending = stakes[msg.sender].rewardDebt;
        require(pending > 0, "no rewards");
        stakes[msg.sender].rewardDebt = 0;
        rewardToken.transfer(msg.sender, pending);
        emit RewardClaimed(msg.sender, pending);
    }

    function pendingRewards(address user) external view returns (uint256) {
        StakeInfo memory info = stakes[user];
        uint256 acc = accRewardPerToken;
        if (totalStaked > 0) {
            acc += ((block.timestamp - info.lastUpdated) * rewardRatePerSecond * 1e18) / totalStaked;
        }
        return (info.balance * acc) / 1e18 - info.rewardDebt;
    }

    function _updateRewards(address user) internal {
        if (totalStaked > 0) {
            accRewardPerToken += ((block.timestamp - stakes[user].lastUpdated) * rewardRatePerSecond * 1e18) / totalStaked;
        }
        if (user != address(0)) {
            StakeInfo storage info = stakes[user];
            uint256 accumulated = (info.balance * accRewardPerToken) / 1e18;
            info.rewardDebt = accumulated > info.rewardDebt ? accumulated - info.rewardDebt : 0;
            info.lastUpdated = block.timestamp;
        }
    }
}
