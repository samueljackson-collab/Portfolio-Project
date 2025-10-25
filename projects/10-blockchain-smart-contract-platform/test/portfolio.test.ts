import { expect } from "chai";
import { ethers } from "hardhat";

describe("PortfolioStaking", () => {
  it("stores staked balance", async () => {
    const [owner, user] = await ethers.getSigners();
    const Token = await ethers.getContractFactory("contracts/mocks/MockToken.sol:MockToken");
    const stakingToken = await Token.deploy("Stake", "STK");
    const rewardToken = await Token.deploy("Reward", "RWD");
    const Staking = await ethers.getContractFactory("PortfolioStaking");
    const staking = await Staking.deploy(stakingToken.address, rewardToken.address);
    await stakingToken.transfer(user.address, ethers.utils.parseEther("10"));
    await stakingToken.connect(user).approve(staking.address, ethers.utils.parseEther("5"));
    await staking.connect(user).stake(ethers.utils.parseEther("5"));
    expect(await staking.totalStaked()).to.equal(ethers.utils.parseEther("5"));
  });
});
