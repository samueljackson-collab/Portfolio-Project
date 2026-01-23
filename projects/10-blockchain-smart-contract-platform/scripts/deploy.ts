import { ethers } from "hardhat";
import * as fs from "fs";
import * as path from "path";

interface DeploymentAddresses {
  tokenAddress?: string;
  rewardTokenAddress?: string;
}

interface GasUsageEntry {
  label: string;
  txHash: string;
  gasUsed: string;
}

async function main() {
  const [deployer] = await ethers.getSigners();
  console.log("Deploying contracts with account:", deployer.address);
  console.log("Account balance:", (await deployer.getBalance()).toString());

  // Load existing deployment addresses if available
  const deploymentFile = path.join(__dirname, "../deployments.json");
  let addresses: DeploymentAddresses = {};

  if (fs.existsSync(deploymentFile)) {
    addresses = JSON.parse(fs.readFileSync(deploymentFile, "utf8"));
    console.log("Loaded existing deployment addresses");
  }

  // Deploy token contract if not already deployed
  let tokenAddress = addresses.tokenAddress;
  const gasUsage: GasUsageEntry[] = [];
  if (!tokenAddress || !ethers.utils.isAddress(tokenAddress)) {
    console.log("\nDeploying ERC20 Token contract...");
    const Token = await ethers.getContractFactory("PortfolioToken");
    const token = await Token.deploy("Portfolio Token", "PTK", ethers.utils.parseEther("1000000"));
    await token.deployed();
    const tokenReceipt = await token.deployTransaction.wait();
    tokenAddress = token.address;
    console.log("✓ Portfolio Token deployed to:", tokenAddress);
    gasUsage.push({
      label: "PortfolioToken deployment",
      txHash: token.deployTransaction.hash,
      gasUsed: tokenReceipt.gasUsed.toString(),
    });
  } else {
    console.log("✓ Using existing Token at:", tokenAddress);
  }

  // Deploy reward token contract if not already deployed
  let rewardTokenAddress = addresses.rewardTokenAddress;
  if (!rewardTokenAddress || !ethers.utils.isAddress(rewardTokenAddress)) {
    console.log("\nDeploying Reward Token contract...");
    const RewardToken = await ethers.getContractFactory("PortfolioToken");
    const rewardToken = await RewardToken.deploy("Reward Token", "RWD", ethers.utils.parseEther("1000000"));
    await rewardToken.deployed();
    const rewardReceipt = await rewardToken.deployTransaction.wait();
    rewardTokenAddress = rewardToken.address;
    console.log("✓ Reward Token deployed to:", rewardTokenAddress);
    gasUsage.push({
      label: "RewardToken deployment",
      txHash: rewardToken.deployTransaction.hash,
      gasUsed: rewardReceipt.gasUsed.toString(),
    });
  } else {
    console.log("✓ Using existing Reward Token at:", rewardTokenAddress);
  }

  // Deploy staking contract with actual token addresses
  console.log("\nDeploying Staking contract...");
  const Staking = await ethers.getContractFactory("PortfolioStaking");
  const staking = await Staking.deploy(tokenAddress, rewardTokenAddress);
  await staking.deployed();
  const stakingReceipt = await staking.deployTransaction.wait();
  console.log("✓ Staking contract deployed to:", staking.address);
  gasUsage.push({
    label: "PortfolioStaking deployment",
    txHash: staking.deployTransaction.hash,
    gasUsed: stakingReceipt.gasUsed.toString(),
  });

  // Save deployment addresses
  const deploymentData = {
    network: (await ethers.provider.getNetwork()).name,
    deployer: deployer.address,
    tokenAddress: tokenAddress,
    rewardTokenAddress: rewardTokenAddress,
    stakingAddress: staking.address,
    gasUsage,
    timestamp: new Date().toISOString(),
  };

  fs.writeFileSync(deploymentFile, JSON.stringify(deploymentData, null, 2));
  console.log("\n✓ Deployment addresses saved to", deploymentFile);

  const evidenceDir = process.env.EVIDENCE_DIR;
  if (evidenceDir) {
    fs.mkdirSync(evidenceDir, { recursive: true });
    fs.writeFileSync(
      path.join(evidenceDir, "deployment-addresses.json"),
      JSON.stringify(deploymentData, null, 2),
    );
    fs.writeFileSync(
      path.join(evidenceDir, "gas-usage-summary.json"),
      JSON.stringify(
        {
          network: deploymentData.network,
          deployer: deploymentData.deployer,
          gasUsage: deploymentData.gasUsage,
          timestamp: deploymentData.timestamp,
        },
        null,
        2,
      ),
    );
    console.log("\n✓ Evidence artifacts saved to", evidenceDir);
  }

  // Verification instructions
  console.log("\n📝 To verify contracts on Etherscan:");
  console.log(`npx hardhat verify --network mainnet ${tokenAddress} "Portfolio Token" "PTK" "1000000000000000000000000"`);
  console.log(`npx hardhat verify --network mainnet ${rewardTokenAddress} "Reward Token" "RWD" "1000000000000000000000000"`);
  console.log(`npx hardhat verify --network mainnet ${staking.address} ${tokenAddress} ${rewardTokenAddress}`);
}

main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
