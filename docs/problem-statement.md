# Problem Statement

## Existing Challenges
1. **Buddy Punching and Time Theft**: Employees routinely clock in for their absent or late colleagues using shared PIN codes or RFID badges. According to the APA, time theft costs employers up to 7% of their total gross payroll.
2. **Data Manipulation**: Traditional databases (SQL/NoSQL) are mutable. A system administrator with database access can alter timestamps, delete logs, or forge records without leaving a technical trace.
3. **Hygiene & Hardware Decay**: Fingerprint scanners require physical contact, leading to hygiene concerns (especially post-pandemic) and frequent hardware failure due to dirty sensors.
4. **Manual Override Chaos**: When an employee forgets their badge, the process of manually overriding or creating a check-in is tedious, undocumented, and prone to abuse.

## Pain Points
* **HR Departments**: Spend days manually reconciling conflicting attendance data at the end of every payroll cycle.
* **Employees**: Experience bottlenecks at entry gates when manual processes slow down throughput during the morning rush.
* **Compliance Auditors**: Cannot definitively prove that an attendance log was not maliciously altered after the fact.

## Limitations of Current Approaches
* **Basic Facial Recognition**: Most off-the-shelf camera systems use rudimentary 2D matching that can be defeated by holding up a printed photograph of an employee (spoofing).
* **Stand-alone Solutions**: Many biometrics systems do not integrate directly into complex shift-management logic (grace periods, buffer minutes, auto-break deductions).

## Consequences of Not Solving the Problem
Failure to modernize the attendance infrastructure results in perpetual payroll leakage. Furthermore, in sectors requiring strict compliance and auditability, relying on mutable databases exposes the organization to severe legal and regulatory liabilities.
