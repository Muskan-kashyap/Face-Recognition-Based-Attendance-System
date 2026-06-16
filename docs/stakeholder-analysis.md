# Stakeholder Analysis

## Primary Stakeholders
1. **Human Resources (HR) Directors**
   * **Needs**: Accurate, automated time-tracking without discrepancies.
   * **Expectations**: Zero manual reconciliation. Seamless integration of dynamic shift buffers and grace periods.
   * **Interaction**: Reviewing monthly growth summaries, overriding critical errors.
2. **Employees / Workforce**
   * **Needs**: A frictionless way to clock in that respects their privacy.
   * **Expectations**: Not having their actual photos stored permanently. Fast check-ins that don't make them late for their shifts.
   * **Interaction**: Daily check-ins via Edge devices; using the employee portal to view their own logs.
3. **System Administrators (SuperAdmins)**
   * **Needs**: A secure, highly available system that is easy to deploy and monitor.
   * **Expectations**: Toggleable heavy features (like Blockchain anchoring) to control cloud costs. Clear logs and robust fail-open mechanisms.

## Secondary Stakeholders
1. **Compliance Auditors**
   * **Needs**: Immutable proof that an attendance record existed at a specific point in time and has not been altered.
   * **Expectations**: Ability to query the Ethereum blockchain using a transaction hash to verify the SHA-256 fingerprint of an attendance row.
2. **Finance / Payroll Department**
   * **Needs**: Clean, structured data on exact hours worked, deductions for breaks, and late arrivals.
   * **Expectations**: API access or CSV exports that integrate directly into systems like Workday or ADP.
