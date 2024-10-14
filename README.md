# BookKeeper
## Transactions
- ?from/to?
- value
- ?account?
- datetime? need other name
- external id
## Source Informartion
the file, api, or manual input from where the transaction is created.
## Classification
### Accounts (categories)
- name
- type
- detail type
- description
#### Type
- revenue
- expenses
- assets
- liabilities
- ?equity?

## Functional Requirements
### Multi-Channel Data Input
The system must support file and manual data input through both a web interface and an API, with logs of input creation. Files should be stored, and transactions must reference the corresponding creation log.

### Uploads and Transactions Visualization
The system must provide a view of uploaded files and the transactions they generate, with detailed history, filtering, and search capabilities.

### Archive and Delete Data
The system must allow users to archive or permanently delete files and transactions, with confirmation steps to prevent accidental loss.

### Database Logging
All operations (creation, update, deletion, archiving) must be logged in the database, capturing user actions, timestamps, and operation details for traceability.

## Non-functional Requirements
