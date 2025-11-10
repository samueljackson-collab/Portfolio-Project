import { ethers } from "hardhat";

async function main() {
  const [deployer] = await ethers.getSigners();
  console.log("Deploying with", deployer.address);

  const Staking = await ethers.getContractFactory("PortfolioStaking");
  const staking = await Staking.deploy(
    "0x0000000000000000000000000000000000000001",
    "0x0000000000000000000000000000000000000002"
  );
  await staking.deployed();
  console.log("Staking deployed to", staking.address);
}

main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
