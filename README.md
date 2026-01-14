# User Interaction Predictor (UIP)

The **User Interaction Predictor** is a core component designed to facilitate structured and reproducible algorithmic audits. Its primary function is to simulate artificial user behavior within "For You" recommendation feeds across various social media platforms.

This project is developed as part of the [KInIT AI-Auditology](https://kinit.sk/project/ai-auditology-social-media-ai-algorithms-auditing/) initiative, focusing on auditing social media AI algorithms.

> **Note:** Note: Version 0.1.0 is intended for testing purposes. Current interaction generation uses stochastic modeling (mocked behavior) to simulate human-like sequences.

## Architecture & Integration
To utilize the predictor effectively, users should be familiar with **sockpuppeting auditing** techniques. The system requires a frontend agent to execute the actions returned in the HTTP response.

*Recommendation: Implement a slight delay before executing actions to better replicate human cognitive processing.*

### Supported Platforms
- **YouTube** (Availability check enabled)
- **TikTok** (Availability check enabled)
- **Instagram** (Availability check restricted - see configuration)

## Getting Started

### Prerequisites
- **Python:** >= 3.11
- **Package Manager:** pip
- **Version Control:** git

### Local Installation & Execution
1. **Clone the repository:**
    ```bash
   git clone <https://github.com/erikmacak/user-interaction-predictor.git>
2. **Navigate to the backend directory:**
    ```bash
    cd src/backend
3. **Initialize Virtual Environment:**
    ```bash
    python -m venv .venv
    source .venv/bin/activate  # On Windows: .venv\Scripts\activate
4. **Install Dependencies:**
    ```bash
    pip install -e .[dev]
5. **Run tests to verify successful installation:**
    ```bash
    pytest tests/ -v
6. **Start Development Server:**
    ```bash
    fastapi dev main.py
*Note: If your IDE highlights fastAPI related imports as unresolved, set your Python Interpreter to **./src/backend/.venv/Scripts/python.exe**.*

## API Specification
- **Endpoint:** `POST /predict_actions`

- **Request Body (example values):**
```json
{
  "platform": "YouTube",
  "video_id": "HuYR_pdHSBU"
}
```

Allowed values for `platform`: "YouTube", "TikTok", "Instagram".

- **Response Body (example values):**
```json
{
  "predicted_actions": [
    { "action": "LIKE" },
    { "action": "SKIP" }
  ]
}
```

Possible actions: **LIKE, FOLLOW, SKIP, FINISH_WATCHING, REWATCH**. The **SKIP** action is always included to ensure sequence termination.

## Configuration & Known Issues

### Instagram Integration

Due to platform-specific API limitations, the availability check for Instagram is disabled by default.

To enable Instagram support: Open `src/backend/core/settings.py` and set:

```py
allow_instagram_without_availability_check = True
```

If a non-existent `video_id` with platform value of 'Instagram' is provided, the system may exhibit unstable behavior in future releases.

### Performance

Latency: Estimated response time is 0.5s – 2.0s for YouTube/TikTok (includes availability validation). Instagram requests are processed near-instantly.

Versions: Computing logic versioning can be toggled in `settings.py` (default: v1).