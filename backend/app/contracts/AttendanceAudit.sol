// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

/**
 * @title AttendanceAudit
 * @dev Immutable append-only store for auditing face recognition attendance logs.
 * Prevents retrospective data manipulation by database administrators.
 */
contract AttendanceAudit {
    
    struct AuditRecord {
        string recordHash;    // SHA-256 hash of the complete attendance record
        uint256 blockNumber; // Block number when anchored
        uint256 timestamp;   // Timestamp of transaction
        address anchorer;    // Address of the node/service that anchored the record
    }

    // Mapping from unique database reference ID to AuditRecord
    mapping(uint256 => AuditRecord) private _records;
    
    // Admin/Owner address allowed to write records
    address public owner;
    
    // System status
    bool public isPaused;

    // Events
    event RecordAnchored(uint256 indexed refId, string recordHash, address indexed anchorer, uint256 blockNumber);
    event ContractPausedStateChanged(bool isPausedState);
    event OwnerTransferred(address indexed oldOwner, address indexed newOwner);

    modifier onlyOwner() {
        require(msg.sender == owner, "AttendanceAudit: caller is not the owner");
        _;
    }

    modifier whenNotPaused() {
        require(!isPaused, "AttendanceAudit: operations are currently paused");
        _;
    }

    constructor() {
        owner = msg.sender;
        isPaused = false;
    }

    /**
     * @notice Anchors an attendance log hash to the blockchain.
     * @param refId Unique ID of the database attendance log row.
     * @param recordHash SHA-256 hash of the row content.
     */
    function anchorRecord(uint256 refId, string calldata recordHash) external onlyOwner whenNotPaused {
        require(bytes(recordHash).length == 64, "AttendanceAudit: hash must be exactly 64 characters (SHA-256)");
        require(bytes(_records[refId].recordHash).length == 0, "AttendanceAudit: record already anchored");

        _records[refId] = AuditRecord({
            recordHash: recordHash,
            blockNumber: blockNumber(),
            timestamp: blockTimestamp(),
            anchorer: msg.sender
        });

        emit RecordAnchored(refId, recordHash, msg.sender, blockNumber());
    }

    /**
     * @notice Checks the integrity of a database record against the blockchain anchor.
     * @param refId Unique ID of the database log.
     * @param recordHash Current computed hash of the database log.
     * @return true if the hash matches the anchored hash, false otherwise.
     */
    function verifyRecord(uint256 refId, string calldata recordHash) external view returns (bool) {
        if (bytes(_records[refId].recordHash).length == 0) {
            return false;
        }
        return keccak256(abi.encodePacked(_records[refId].recordHash)) == keccak256(abi.encodePacked(recordHash));
    }

    /**
     * @notice Fetches anchoring details of a record.
     * @param refId Unique ID of the database log.
     */
    function getRecordDetails(uint256 refId) external view returns (
        string memory recordHash,
        uint256 blockNo,
        uint256 timeLogged,
        address anchorer
    ) {
        AuditRecord memory record = _records[refId];
        require(bytes(record.recordHash).length > 0, "AttendanceAudit: record not found");
        return (record.recordHash, record.blockNumber, record.timestamp, record.anchorer);
    }

    // Helper view functions for testing
    function blockNumber() internal view virtual returns (uint256) {
        return block.number;
    }

    function blockTimestamp() internal view virtual returns (uint256) {
        return block.timestamp;
    }

    // Control operations
    function setPaused(bool paused) external onlyOwner {
        isPaused = paused;
        emit ContractPausedStateChanged(paused);
    }

    function transferOwnership(address newOwner) external onlyOwner {
        require(newOwner != address(0), "AttendanceAudit: new owner cannot be the zero address");
        emit OwnerTransferred(owner, newOwner);
        owner = newOwner;
    }
}
