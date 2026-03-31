# Architecture

## Overview

The system consists of three main components:
 
1. **Execution Agent**
2. **User Interaction Predictor (UIP)**
3. **Visualization Layer**

---

## Data Flow

1. Agent sends request → `/predict_actions`
2. UIP processes video:
   - Evaluates video virality and engagement metrics from available metadata
   - Downloads segment
   - Extracts frames
   - Identifies audio
3. LLM evaluates content
4. Decision engine computes actions
   - Applies agent-specific audit scenarios to simulate target user personas
   - References global social media consumption patterns and *"For You"* feeds
   - Derives optimal interactions from the LLM’s qualitative content evaluation
5. Response returned to agent
6. Agent executes actions

---

## Internal Pipeline

### 1. Video Processing

- Segment download (based on duration)
- Frame extraction (OpenCV)
- Audio recognition (ShazamAPI)

---

### 2. Feature Extraction

- Metadata analysis
- Engagement estimation
- Content classification

---

### 3. LLM Evaluation

Using configured LLM:

- Topic detection
- Emotion analysis
- Quality assessment
- Behavioral relevance

---

### 4. Decision Engine

Custom pipeline that:

- Interprets LLM output
- Applies behavioral logic
- Returns optimal interaction

---

### 5. Iterative Analysis

- First segment analyzed
- If no `SKIP` → continue
- Stops when skip condition met

---

## TikTok-specific Handling

Due to platform limitations, TikTok does not support downloading specific video segments directly from the server.

As a result, the processing pipeline differs slightly:
- The full video is downloaded
- Based on its duration, multiple frames are extracted (typically 8–10)
- The remaining analysis pipeline remains identical to other platforms

Unlike other platforms where multiple segments may be analyzed, TikTok videos are treated as a single segment.

Despite this difference, prediction accuracy remains consistently high.