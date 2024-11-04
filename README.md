# tributary

Backend infrastructure powering Ford's sensor streaming system. A Flask server acts as a data ingestion layer, recording sensor data to a Redis database. The system exposes two REST APIs: 
/record for sensor data submission and /collect for user data retrieval.
