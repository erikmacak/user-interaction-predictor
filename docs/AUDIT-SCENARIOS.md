# Audit Scenarios (User Profiles)

## Importance

User profile definition is the **most critical input**.

Poor profile -> unrealistic behavior  
Well-defined profile -> high-quality simulation

---

## Best Practices

- 8–12 preferred emotions
- 1–2 languages
- 4–7 interest topics

---

## Example

```json
{
  "user_profile": {
    "user_email": "john.techie@gmail.com",
    "gender": "male",
    "country_code": "us",
    "date_of_birth": "15.03.1998",
    "favorite_authors": ["mrbeast"],
    "retention_triggers": {
      "preferred_emotions": [
        "curiosity",
        "amusement",
        "surprise"
      ],
      "preferred_languages": ["en"],
      "interest_topics": [
        "artificial_intelligence",
        "coding_tutorials"
      ]
    }
  }
}
```

The following example illustrates the required data format. When creating audit scenarios, strictly adhere to the structure shown above and apply the provided best practices.

## Warning

Overly complex profiles may lead to:
 + Excessive engagement actions
 + Unrealistic behavior patterns