# Kuiper System/Network Administrator - Video & Learning Resources

**Purpose:** Curated list of videos and online resources for interview preparation
**Usage:** Watch videos alongside labs to reinforce learning
**Last Updated:** 2025-11-10

---

## How to Use This Resource

1. **Videos are organized by topic** - watch based on your learning path schedule
2. **Mix video + hands-on** - watch video first, then do corresponding lab
3. **Take notes** - pause videos to write down key concepts
4. **Rewatch tough sections** - complex topics may need 2-3 viewings
5. **YouTube playback speed** - 1.25x or 1.5x can save time once you grasp basics

---

## AWS Networking & VPC

### AWS Official

1. **AWS VPC Beginner to Advanced**
   - Platform: Udemy
   - Link: https://www.udemy.com/course/networking-in-aws/
   - Content: VPC Peering, VPC Endpoint/PrivateLink, Transit Gateway, VPN connection, Direct Connect
   - Labs: 20+ hands-on exercises
   - Cost: Paid (~$10-20 on sale)
   - **Best For:** Week 1, Days 2-3 (VPC fundamentals)

2. **AWS Networking Masterclass - Amazon VPC & Hybrid Cloud 2025**
   - Platform: Udemy
   - Link: https://www.udemy.com/course/aws-networking-amazon-vpc-aws-vpn-hybrid-cloud/
   - Content: Highly visual approach with diagrams and animations
   - **Best For:** Week 1, comprehensive review

3. **AWS Official Documentation - VPC**
   - Link: https://docs.aws.amazon.com/vpc/latest/userguide/
   - Content: Complete VPC user guide with examples
   - Free: Yes
   - **Best For:** Reference material throughout 2 weeks

### Community Content

4. **AWS Networking 101** (Blog Series)
   - Link: https://blog.ipspace.net/2020/05/aws-networking-101/
   - Content: Deep technical dive into AWS networking concepts
   - Free: Yes
   - **Best For:** Week 1, Days 2-5 (foundational reading)

---

## Transit Gateway

### AWS Official

5. **AWS Transit Gateway Tutorials**
   - Link: https://docs.aws.amazon.com/vpc/latest/tgw/tgw-getting-started.html
   - Content: Official getting started tutorials
   - Interactive: CLI and Console examples
   - Free: Yes
   - **Best For:** Week 1, Day 3 (Lab 03)

6. **How AWS Transit Gateway Works**
   - Link: https://docs.aws.amazon.com/vpc/latest/tgw/how-transit-gateways-work.html
   - Content: Architectural overview, use cases, route tables
   - Free: Yes
   - **Best For:** Week 1, Day 3 (pre-lab reading)

### Community Content

7. **SubnetSavy Transit Gateway Guide 2025**
   - Link: https://subnetsavy.com/wp-content/uploads/articles/aws-transit-gateway-explained.html
   - Content: Step-by-step setup, route tables, security, hybrid cloud
   - Free: Yes
   - **Best For:** Week 1, Day 3 (supplemental reading)

8. **Tutorials Dojo Cheat Sheet (Nov 2024)**
   - Link: https://tutorialsdojo.com/aws-transit-gateway/
   - Content: Comprehensive concepts summary
   - Free: Yes
   - **Best For:** Quick reference, study breaks

---

## BGP (Border Gateway Protocol)

### Video Resources

9. **TechTarget: An Overview of How BGP Works** (Video)
   - Link: https://www.techtarget.com/searchnetworking/video/An-overview-of-how-BGP-works
   - Content: Animated explanation of BGP routing
   - Length: ~5-10 minutes
   - Free: Yes
   - **Best For:** Week 1, Day 4 (BGP introduction)

### Written Tutorials (Beginner-Friendly)

10. **Beginner's Guide to Understanding BGP** (CDemi.io)
    - Link: https://blog.cdemi.io/beginners-guide-to-understanding-bgp/
    - Content: Fundamentals, Autonomous Systems, peering
    - Free: Yes
    - **Best For:** Week 1, Day 4 (before Lab 04)

11. **NetworkLessons.com - BGP Course**
    - Link: https://networklessons.com/bgp
    - Content: Comprehensive BGP course from basics to advanced
    - Free: Partial (some lessons free, full course requires subscription)
    - **Best For:** Week 1, Days 4-5 (deep dive)

12. **Kentik BGP Tutorial**
    - Link: https://www.kentik.com/kentipedia/bgp-routing/
    - Content: BGP basics, routes, peers, paths, advertising, configuration
    - Free: Yes
    - **Best For:** Week 1, Day 4 (BGP theory)

13. **DigitalTut: Border Gateway Protocol BGP Tutorial**
    - Link: https://www.digitaltut.com/border-gateway-protocol-bgp-tutorial
    - Content: BGP path selection, attributes, troubleshooting
    - Free: Yes
    - **Best For:** Week 1, Day 5 (BGP traffic engineering)

---

## AWS Site-to-Site VPN

### AWS Official

14. **Get Started with AWS Site-to-Site VPN**
    - Link: https://docs.aws.amazon.com/vpn/latest/s2svpn/SetUpVPNConnections.html
    - Content: Official setup guide
    - Free: Yes
    - **Best For:** Week 1, Days 4-5 (Lab 04)

15. **AWS Site-to-Site VPN Routing Options**
    - Link: https://docs.aws.amazon.com/vpn/latest/s2svpn/VPNRoutingTypes.html
    - Content: Static vs Dynamic (BGP) routing
    - Free: Yes
    - **Best For:** Week 1, Day 4 (understanding BGP over VPN)

### Hands-On Tutorials

16. **Medium: Setting up a Dynamic, BGP-Based, Hybrid Site-to-Site VPN in AWS**
    - Link: https://medium.com/@hong.howie/setting-up-a-dynamic-bgp-based-hybrid-site-to-site-vpn-in-aws-47c6c8a752b2
    - Content: Walkthrough of creating HA, dynamic, BGP-based VPN
    - Free: May require Medium membership
    - **Best For:** Week 1, Day 5 (Lab 04 reference)

17. **Edge Cloud: AWS Site-to-Site VPN with StrongSwan & FRRouting**
    - Link: https://www.edge-cloud.net/2019/07/18/aws-site-2-site-vpn-with-strongswan-frrouting/
    - Content: EC2-based VPN endpoint with StrongSwan (IPsec) and FRRouting (BGP)
    - Free: Yes
    - **Best For:** Week 1, Day 4-5 (if using StrongSwan for Lab 04)

18. **VyOS AWS Site-to-Site VPN and BGP** (PDF Guide)
    - Link: https://vyos.io/documents/aws-partnership/VyOS—AWS-Site-to-Site-VPN-and-BGP.pdf
    - Content: VyOS configuration for AWS VPN with BGP
    - Free: Yes
    - **Best For:** Week 1, Days 4-5 (if using VyOS for Lab 04)

19. **AWS Workshop: Establish Site-to-Site VPN Connection**
    - Link: https://getstarted.awsworkshop.io/02-dev-fast-follow/03-network-integration/01-on-premises-network-integration/04-set-up-site-to-site-vpn.html
    - Content: Formal workshop guide with step-by-step instructions
    - Free: Yes
    - **Best For:** Week 1, Days 4-5 (Lab 04)

---

## AWS Direct Connect

### AWS Official

20. **AWS Direct Connect Documentation**
    - Link: https://docs.aws.amazon.com/directconnect/
    - Content: Complete guide to Direct Connect
    - Free: Yes
    - **Best For:** Week 1, Day 6 (understanding DX vs VPN)

21. **AWS Direct Connect Video Catalog**
    - Link: https://awsvideocatalog.com/networking_&_content_delivery/direct_connect/
    - Content: Collection of Direct Connect videos
    - Free: Yes
    - **Best For:** Week 1, reference as needed

22. **AWS VPC Connectivity Options (Whitepaper)**
    - Link: https://docs.aws.amazon.com/whitepapers/latest/aws-vpc-connectivity-options/
    - Content: Comprehensive guide covering VPN, DX, Transit Gateway, Cloud WAN
    - Free: Yes
    - **Best For:** Week 1-2, architectural reference

---

## Route 53

### AWS Official

23. **AWS Route 53 Developer Guide**
    - Link: https://docs.aws.amazon.com/Route53/latest/DeveloperGuide/
    - Content: Complete DNS and routing policy documentation
    - Free: Yes
    - **Best For:** Week 1, Day 6 (Lab 05)

24. **Route 53 Routing Policies**
    - Link: https://docs.aws.amazon.com/Route53/latest/DeveloperGuide/routing-policy.html
    - Content: Latency, geolocation, failover, weighted, multivalue
    - Free: Yes
    - **Best For:** Week 1, Day 6 (Lab 05 prep)

---

## Satellite Internet (LEO, Kuiper, Starlink)

### Overviews

25. **Amazon Project Kuiper vs SpaceX Starlink**
    - Link: https://www.spacelaunchschedule.com/news/the-satellite-internet-race-amazon-project-kuiper-vs-starlink/
    - Content: Comparison of technologies, timelines, architectures
    - Free: Yes
    - **Best For:** Week 1, Day 1 (Kuiper context)

26. **Project Kuiper: Amazon's Answer to SpaceX's Starlink**
    - Link: https://www.space.com/project-kuiper-passes-crucial-test
    - Content: Recent test results, technology details
    - Free: Yes
    - **Best For:** Week 1, Day 1

27. **Starlink Technology Page**
    - Link: https://starlink.com/technology
    - Content: Official Starlink technology overview (useful for understanding LEO satellite systems)
    - Free: Yes
    - **Best For:** Week 1, Day 1 (LEO satellite concepts)

28. **What is Starlink? Everything You Need to Know**
    - Link: https://www.techtarget.com/whatis/definition/Starlink
    - Content: LEO satellites, phased arrays, OISL, latency comparison to GEO
    - Free: Yes
    - **Best For:** Week 1, Day 1

29. **The Noob's Guide to Starlink**
    - Link: https://ig.space/commslink/the-noobs-guide-to-starlink-background-and-practical-satellite-internet/
    - Content: Background and practical overview of satellite internet
    - Free: Yes
    - **Best For:** Week 1, Day 1 (beginner-friendly)

30. **How Does Satellite Internet Work? (NordVPN Blog)**
    - Link: https://nordvpn.com/blog/how-does-satellite-internet-work/
    - Content: LEO vs GEO comparison, latency, how signals travel
    - Free: Yes
    - **Best For:** Week 1, Day 1

---

## AWS re:Invent Sessions (Networking)

### 2024 Sessions

31. **AWS re:Invent 2024 Networking Journey Blog**
    - Link: https://aws.amazon.com/blogs/networking-and-content-delivery/charting-your-aws-networking-journey-at-reinvent-2024/
    - Content: Overview of all networking sessions (NET311, Hybrid Connectivity, Cloud WAN)
    - Free: Yes
    - **Best For:** Week 2 (advanced topics)

32. **NET311 - Build Scalable, Secure, Global Connectivity with AWS**
    - Content: Best practices for AWS Verified Access, Client VPN, Direct Connect
    - Free: Yes (if recording available on AWS YouTube)
    - **Best For:** Week 2, Days 10-11 (HA architecture)

33. **Hybrid Connectivity Chalk Talk**
    - Content: HA and DR using Direct Connect, Site-to-Site VPN, Transit Gateway
    - Free: Yes (if recording available)
    - **Best For:** Week 2, Days 10-11 (Lab 08 reference)

**Note:** re:Invent session videos are typically published on the AWS YouTube channel and AWS re:Invent site 2-4 weeks after the conference. Search for "AWS re:Invent 2024 networking" on YouTube.

---

## Monitoring & Observability

### SRE Concepts

34. **Google SRE Book - Service Level Objectives Chapter**
    - Link: https://sre.google/sre-book/service-level-objectives/
    - Content: SLI/SLO/SLA concepts, error budgets, monitoring best practices
    - Free: Yes (full book online)
    - **Best For:** Week 2, Day 8 (before Lab 06)

35. **Google SRE Workbook - Implementing SLOs**
    - Link: https://sre.google/workbook/implementing-slos/
    - Content: Practical guide to implementing SLOs
    - Free: Yes
    - **Best For:** Week 2, Days 8-9 (Lab 06, Lab 15)

36. **Atlassian: SLA vs SLO vs SLI**
    - Link: https://www.atlassian.com/incident-management/kpis/sla-vs-slo-vs-sli
    - Content: Clear explanation of differences
    - Free: Yes
    - **Best For:** Week 2, Day 8

### AWS Monitoring

37. **Monitor AWS Site-to-Site VPN Tunnels with CloudWatch**
    - Link: https://aws.amazon.com/blogs/networking-and-content-delivery/monitor-your-aws-site-to-site-vpn-tunnels-with-amazon-cloudwatch/
    - Content: VPN monitoring best practices, key metrics
    - Free: Yes
    - **Best For:** Week 2, Day 8 (Lab 06)

38. **AWS CloudWatch Documentation**
    - Link: https://docs.aws.amazon.com/cloudwatch/
    - Content: Complete monitoring documentation
    - Free: Yes
    - **Best For:** Week 2, Day 8 (reference)

### Prometheus & Alertmanager

39. **Prometheus Getting Started**
    - Link: https://prometheus.io/docs/prometheus/latest/getting_started/
    - Content: Official Prometheus tutorial
    - Free: Yes
    - **Best For:** Week 2, Day 11 (if doing Lab 09)

40. **Prometheus Alertmanager Documentation**
    - Link: https://prometheus.io/docs/alerting/latest/alertmanager/
    - Content: Routing, grouping, silencing, inhibition
    - Free: Yes
    - **Best For:** Week 2, Day 11 (Lab 09)

41. **Blackbox Exporter GitHub**
    - Link: https://github.com/prometheus/blackbox_exporter
    - Content: Synthetic monitoring with Prometheus
    - Free: Yes
    - **Best For:** Week 2, Day 8-9 (synthetic probes)

---

## Security & PKI

### mTLS & Certificates

42. **Getting Started with Mutual TLS (mTLS)**
    - Link: https://medium.com/@awkwardferny/getting-started-with-mutual-tls-mtls-3b2b4e6d2e66
    - Content: mTLS basics, certificate generation, testing
    - Free: May require Medium membership
    - **Best For:** Week 2, Day 9 (Lab 07)

43. **OpenSSL Certificate Authority Tutorial**
    - Link: https://jamielinux.com/docs/openssl-certificate-authority/
    - Content: Setting up a private CA with OpenSSL
    - Free: Yes
    - **Best For:** Week 2, Day 9 (Lab 07)

44. **AWS Certificate Manager Private CA User Guide**
    - Link: https://docs.aws.amazon.com/privateca/latest/userguide/
    - Content: AWS-managed private CA service
    - Free: Yes
    - **Best For:** Week 2, Day 9 (alternative to self-managed CA)

---

## Chaos Engineering

### Principles & Practice

45. **Principles of Chaos Engineering**
    - Link: https://principlesofchaos.org/
    - Content: Foundational chaos engineering principles
    - Free: Yes
    - **Best For:** Week 2, Day 12 (before Lab 13)

46. **AWS Blog: Chaos Engineering on AWS**
    - Link: https://aws.amazon.com/blogs/architecture/chaos-engineering-on-aws/
    - Content: AWS-specific chaos engineering practices
    - Free: Yes
    - **Best For:** Week 2, Day 12 (Lab 13)

47. **Netflix Tech Blog: Chaos Engineering**
    - Link: https://netflixtechblog.com/tagged/chaos-engineering
    - Content: Real-world chaos engineering at scale
    - Free: Yes
    - **Best For:** Week 2, Day 12 (advanced reading)

---

## Automation & IaC

### Terraform

48. **Terraform AWS Provider Documentation**
    - Link: https://registry.terraform.io/providers/hashicorp/aws/latest/docs
    - Content: Complete AWS resource documentation for Terraform
    - Free: Yes
    - **Best For:** Throughout 2 weeks (reference)

49. **Terraform Module Development**
    - Link: https://developer.hashicorp.com/terraform/language/modules/develop
    - Content: Writing reusable Terraform modules
    - Free: Yes
    - **Best For:** Week 2, Day 11 (if doing Lab 10)

### Ansible

50. **Ansible Network Automation Documentation**
    - Link: https://docs.ansible.com/ansible/latest/network/index.html
    - Content: Ansible for network device automation
    - Free: Yes
    - **Best For:** Week 2 (if doing Lab 11)

51. **NAPALM Documentation**
    - Link: https://napalm.readthedocs.io/en/latest/
    - Content: Multi-vendor network automation library
    - Free: Yes
    - **Best For:** Week 2 (if doing Lab 11)

---

## YouTube Channels to Subscribe To

### Recommended Channels

52. **AWS Online Tech Talks**
    - Link: https://www.youtube.com/@AWSOnlineTechTalks
    - Content: Weekly AWS webinars and deep dives
    - **Best For:** Ongoing learning

53. **Amazon Web Services (Official)**
    - Link: https://www.youtube.com/@amazonwebservices
    - Content: re:Invent sessions, tutorials, announcements
    - **Best For:** Throughout 2 weeks

54. **NetworkChuck**
    - Link: https://www.youtube.com/@NetworkChuck
    - Content: Networking tutorials (BGP, VLANs, subnetting) in beginner-friendly style
    - **Best For:** Week 1, networking refresher

55. **David Bombal**
    - Link: https://www.youtube.com/@davidbombal
    - Content: Networking, cybersecurity, cloud
    - **Best For:** Week 1-2, supplemental learning

---

## Study Tips for Video Learning

### Effective Video Learning

1. **Active Watching:**
   - Take notes while watching
   - Pause to draw diagrams
   - Repeat difficult sections immediately

2. **Playback Speed:**
   - 1.0x for new, complex concepts
   - 1.25x for review or familiar topics
   - 1.5x for intro/overview sections

3. **Apply Immediately:**
   - Watch video → do related lab within 24 hours
   - Don't binge videos without practice

4. **Create Summaries:**
   - After each video, write 3-5 key takeaways
   - Explain to yourself (or webcam) what you learned

### Avoid Common Pitfalls

❌ **Don't:** Watch 10 hours of videos without doing labs (passive learning doesn't stick)
✅ **Do:** Watch 1 hour → Lab 2 hours → Apply knowledge

❌ **Don't:** Watch videos while distracted (multitasking kills retention)
✅ **Do:** Focus fully, take notes, pause frequently

❌ **Don't:** Skip videos because you "already know this" (review reinforces knowledge)
✅ **Do:** Watch at 1.5x speed for review, extract new insights

---

## Learning Path Integration

### Week 1
- **Day 1:** Videos 25-30 (Satellite Internet)
- **Day 2:** Videos 1-4 (AWS VPC)
- **Day 3:** Videos 5-8 (Transit Gateway)
- **Day 4:** Videos 9-13 (BGP Fundamentals)
- **Day 5:** Videos 14-19 (AWS VPN with BGP)
- **Day 6:** Videos 20-24 (Direct Connect, Route 53)
- **Day 7:** Review Week 1 videos at 1.5x speed

### Week 2
- **Day 8:** Videos 34-38 (Monitoring, SLOs)
- **Day 9:** Videos 42-44 (mTLS, PKI)
- **Day 10-11:** Videos 22, 31-33 (Hybrid HA Architecture, re:Invent sessions)
- **Day 12:** Videos 45-47 (Chaos Engineering)
- **Day 13-14:** Review all key videos (1.5x speed), focus on weak areas

---

## Community & Support

### Forums & Help

56. **AWS re:Post**
    - Link: https://repost.aws/
    - Content: AWS community Q&A
    - **Best For:** Stuck on AWS-specific issues

57. **Reddit r/aws**
    - Link: https://www.reddit.com/r/aws/
    - Content: Community discussions, troubleshooting
    - **Best For:** Real-world experiences, tips

58. **Reddit r/networking**
    - Link: https://www.reddit.com/r/networking/
    - Content: Networking discussions, BGP troubleshooting
    - **Best For:** BGP and general networking help

59. **AWS Documentation**
    - Link: https://docs.aws.amazon.com/
    - Content: Official AWS documentation (always the source of truth)
    - **Best For:** Throughout 2 weeks (reference)

---

## Cost Note

Most resources listed are **free**. Paid options:
- Udemy courses: $10-20 on sale (sales happen frequently)
- Medium articles: May require membership ($5/month or free with limited articles)

**Budget for 2 weeks:** $0-40 (optional for Udemy courses)

---

## Final Tips

1. **Don't watch everything** - Focus on videos relevant to your current lab
2. **Quality over quantity** - 5 well-understood videos > 50 passively watched
3. **Rewatch is okay** - Complex topics often need 2-3 viewings
4. **Apply immediately** - Watch → Lab → Document (same day)
5. **Adjust speed** - Save time with 1.25-1.5x playback after initial viewing

---

**Happy Learning! 🚀**

---

**Last Updated:** 2025-11-10
**Document:** professional/interview-prep/kuiper/videos/VIDEO-RESOURCES.md
