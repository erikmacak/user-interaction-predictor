# API Reference

## `POST /predict_actions`

### Request

Example values

```json
{
    "session_id": "8f2a19b3-4e21-9c6a-11db-33a92f154e81",
    "video_metadata": {
        "video_id": "XkL9pQmRzWq",
        "video_author": "urban_explorer",
        "video_time_duration": 15,
        "description": "morning routine",
        "hashtags": ["morning", "routing", "fyp"],
        "likes_count": 283000,
        "comments_count": 1256,
        "reposts_count": null,
        "shares_count": null
    }
}
```

### Response

Example values

```json
{
  "predicted_actions": [
    "like",
    "finish_watching",
    "skip"
  ]
}
```

### POSSIBLE ACTIONS
 + LIKE
 + SAVE
 + SKIP
 + FINISH_WATCHING
 + REWATCH
 + CONTINUE_WATCHING_FOR: X seconds

### Notes

More metadata -> better and optimal predictions

Minimum metadata required:
 + session_id
 + video_id
 + video_time_duration