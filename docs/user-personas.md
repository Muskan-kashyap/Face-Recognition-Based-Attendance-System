# User Personas

## 1. SuperAdmin (System Administrator)
* **Role**: Owner of the entire deployment infrastructure.
* **Responsibilities**: Manages system-wide settings, provisions new organizations (tenants), and maintains infrastructure health.
* **Goals**: Keep system uptime at 99.9%. Control infrastructure costs (e.g., toggling Web3 integration).
* **Pain Points**: Dealing with system crashes when a database goes down.
* **Permissions**: Global Access (`SuperAdmin` role).
* **Usage Scenarios**: Toggling `BLOCKCHAIN_ENABLED` via the `/api/v1/admin/settings/blockchain/toggle` endpoint.

## 2. Admin (HR Manager / Operations Lead)
* **Role**: Organization-level manager.
* **Responsibilities**: Manages departments, shifts, and bulk enrolls users. Handles exceptional scenarios.
* **Goals**: Ensure all employees are assigned to the correct shifts with the proper grace periods.
* **Pain Points**: Employees forgetting to clock out, resulting in corrupted payroll data.
* **Permissions**: Full write access to their specific `org_id`.
* **Usage Scenarios**: Using the `ManualOverride` functionality to fix an employee's attendance log if a camera fails.

## 3. Manager (Department Lead)
* **Role**: Leads a specific subset of employees.
* **Responsibilities**: Monitors attendance, approves localized reports.
* **Goals**: Keep their team productive and intervene if burnout metrics spike.
* **Pain Points**: Lack of visibility into remote or distributed team attendance.
* **Permissions**: Read/Write access limited to users where `dept_id` matches their own.
* **Usage Scenarios**: Viewing the `wellness-heatmap` to see if their department is showing aggregate signs of stress or anger based on the DeepFace emotion analysis.

## 4. Employee (End User)
* **Role**: The core user of the system.
* **Responsibilities**: Showing up to work and clocking in/out.
* **Goals**: Get paid accurately for the hours they work.
* **Pain Points**: Long lines at the biometric scanner; anxiety about facial recognition privacy.
* **Permissions**: Read-only access to their own `user_id` data.
* **Usage Scenarios**: Walking up to an Edge device, facing the camera, and walking away. Checking their portal on Friday to ensure their 40 hours were logged correctly.
