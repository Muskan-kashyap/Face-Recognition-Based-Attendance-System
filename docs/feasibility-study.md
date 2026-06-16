# Feasibility Study

## 1. Technical Feasibility
**Status: Highly Feasible**
The architecture leverages mature, open-source AI models (DeepFace) and proven database technologies (PostgreSQL + pgvector). The shift from a monolith to a hybrid proxy architecture (where the ML pipeline is isolated) has successfully mitigated the extreme memory overhead of loading PyTorch directly into the API event loop.

## 2. Operational Feasibility
**Status: Feasible with Training**
Deploying an edge device (like an iPad or a Raspberry Pi kiosk) at physical entryways requires initial hardware setup and network configuration by the IT department. However, once running, the zero-touch nature of facial recognition completely eliminates daily operational overhead for HR.

## 3. Economic Feasibility
**Status: Feasible (Dynamic Costs)**
* **Savings**: Eliminating 5% payroll leakage due to time theft yields immediate ROI.
* **Costs**: Cloud GPU instances (AWS g4dn.xlarge) cost ~$380/month.
* **Blockchain Gas**: Writing to Ethereum Mainnet can be cost-prohibitive (~$1.50 per transaction). To maintain economic feasibility, the system introduced the **SuperAdmin Web3 Toggle**, allowing organizations to anchor to cheaper Layer 2 networks (Polygon, Arbitrum) or disable the feature entirely to save funds while relying on standard DB backups.

## 4. Organizational Feasibility
**Status: Feasible**
Employees may exhibit initial resistance to facial recognition due to privacy concerns. The organizational rollout must emphasize the **Zero-Knowledge** architecture—proving that the company only stores mathematical coordinates, not actual photographs.
