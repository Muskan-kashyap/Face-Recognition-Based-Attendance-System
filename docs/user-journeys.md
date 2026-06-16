# User Journeys

## Journey 1: The Daily Check-In
1. **Trigger**: Employee arrives at the office lobby.
2. **Action**: Employee looks at the edge kiosk (e.g., an iPad running the React frontend).
3. **System**: 
   * Captures the frame.
   * Runs liveness detection to ensure it's not a photo.
   * Extracts embedding.
   * Queries DB to identify the Employee.
   * Logs attendance.
   * Async anchors to Blockchain.
4. **Result**: Screen flashes green with "Welcome, John! (On Time)". Employee walks through the turnstile.

## Journey 2: The HR Manual Override
1. **Trigger**: A power outage prevented an employee from clocking out.
2. **Action**: Admin logs into the SuperAdmin dashboard.
3. **System**: Issues a JWT with `role=Admin`.
4. **Action**: Admin navigates to the Attendance grid, selects the missing log, and inserts a manual "Check-Out" time.
5. **System**: Creates a `ManualOverride` row in the database, tying the `admin_user_id` to the modification for strict auditing, and updates the `AttendanceLog`.

## Journey 3: Scaling Up Infrastructure
1. **Trigger**: Cloud costs for Ethereum gas fees exceed the monthly budget.
2. **Action**: SuperAdmin logs into the dashboard and accesses the Global Settings.
3. **Action**: SuperAdmin toggles "Web3 Anchoring" to OFF.
4. **System**: Calls `POST /api/v1/admin/settings/blockchain/toggle` and updates the `SystemSettings` table.
5. **Result**: The background task instantly switches to "Simulation Mode" (0 cost) without requiring a server reboot.
