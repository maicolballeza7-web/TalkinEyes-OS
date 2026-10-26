# 👁️ TalkinEyes OS — Assistive Communication Through Vision

> **Observe. Understand. Predict. Adapt. Communicate.**

TalkinEyes OS is an assistive communication platform designed for people with
limited mobility who need a reliable, hands-free way to express essential
needs, discomfort, and requests for help.

The system turns intentional eye blinks into accessible menu selections and
spoken communication. It combines local computer vision, personalized
calibration, adaptive interaction, and an emergency-notification boundary
designed for future cloud deployment.
<img width="917" height="362" alt="image" src="https://github.com/user-attachments/assets/b4e04493-cd50-47a4-8a2e-7af97db39bd9" />


## The Problem

Many people with severe motor impairments cannot reliably use a keyboard,
touchscreen, mouse, or conventional augmentative communication device. A
simple request such as *"I need help"* can become dependent on another
person's availability.

Existing assistive interfaces can also be difficult to operate when users
experience:

- Reduced hand or limb control.
- Fatigue or involuntary movement.
- Difficulty maintaining a fixed gaze.
- Different facial anatomy and blink patterns.
- The need to communicate quickly in an emergency.

TalkinEyes focuses on a practical interaction channel that many users can
still control: intentional eye blinks.

## Our Solution

TalkinEyes OS provides a hands-free communication interface controlled through
a standard camera. The system detects facial landmarks, calculates eye
openness, filters accidental movements, and uses a scanning menu to let the
user select a phrase.

The selected phrase can be spoken locally through text-to-speech. The
interface also includes an emergency communication boundary that currently
simulates an AWS SNS alert, allowing the cloud integration to be validated
without requiring production credentials.

The design prioritizes:

- **Local-first operation:** core detection and communication do not require
  an internet connection.
- **Personalization:** calibration adapts detection thresholds to each user.
- **Safety:** head-pose validation and blink-confidence scoring reduce false
  selections.
- **Extensibility:** vision, interaction, intelligence, communication, and
  cloud responsibilities are separated into independent modules.

## Architecture

TalkinEyes OS follows an **Edge + Cloud** architecture.

```text
Camera
  │
  ▼
Edge Vision Layer
  ├── OpenCV: camera capture and frame processing
  ├── MediaPipe: face and eye landmark detection
  ├── EAR analysis: eye openness measurement
  ├── Blink Engine: temporal blink detection
  └── Head Pose: yaw and pitch validation
  │
  ▼
Interaction Layer
  ├── Personalized calibration
  ├── Blink confidence scoring
  ├── Scanning menu
  └── Predictive option ranking
  │
  ├──────────────► Local Text-to-Speech
  │
  └──────────────► AWS Notification Boundary
                         └── SNS emergency alert
```

### Edge layer

The edge layer runs locally on the user's computer:

- **OpenCV** captures and prepares camera frames.
- **MediaPipe Face Mesh** provides facial landmarks around the eyes and face.
- **Eye Aspect Ratio (EAR)** estimates whether the eyes are open or closed.
- **Head-pose estimation** pauses blink selection when the user is not facing
  the screen.
- **Blink confidence** evaluates duration and depth before accepting a
  selection.

Keeping this processing local reduces latency, supports offline use, and
limits the exposure of sensitive camera data.

### Cloud layer

The cloud boundary is represented by an AWS SNS-compatible notifier. In the
current development stage, it prints a structured JSON alert instead of
calling AWS. A production deployment can replace this boundary with an
authenticated AWS SDK integration without coupling cloud code to the vision
pipeline.

## Key Features

### 1. Personalized Calibration 🎯

Every user has a different natural eye-opening range and blink depth. The
calibration flow records open-eye and closed-eye measurements and stores
personalized thresholds in a local profile.

This helps TalkinEyes adapt to differences in:

- Facial anatomy.
- Camera distance.
- Lighting conditions.
- Natural blink strength.

### 2. Head Pose Estimation 🧭

TalkinEyes estimates the user's head orientation using facial landmarks and
`solvePnP`-based pose estimation.

When the user's yaw or pitch exceeds the configured frontal-view threshold,
blink processing is paused. This helps distinguish intentional interaction from
looking away, repositioning, or momentary loss of attention.

### 3. Blink Confidence Scoring 👁️

A blink is not accepted solely because the eyes became smaller in one frame.
The system evaluates temporal and geometric evidence, including:

- Minimum blink duration.
- Eye Aspect Ratio depth.
- Reopening behavior.
- Detection continuity.

This stateful approach helps reduce false positives caused by noise,
involuntary movement, or incomplete landmark detection.

### 4. Predictive Menu Ranking 📊

TalkinEyes stores local selection frequencies in a JSON history file. Frequently
used phrases and categories can be presented earlier in the scanning menu,
reducing interaction time and cognitive load.

The ranking is deterministic and explainable: options are ordered by their
recorded frequency while preserving the relationship between each option and
its visual color.

### 5. AWS Emergency Alerts 🚨

The emergency-notification boundary prepares a structured alert containing:

- Timestamp.
- SNS topic ARN.
- Emergency message.
- Delivery status.

The current implementation simulates the AWS SNS send operation and prints
the formatted JSON to the console. This keeps development safe and
credential-free while preserving a clear integration point for a future
production deployment.

## TalkinEyes V1 vs. TalkinEyes OS

| Capability | TalkinEyes V1 | TalkinEyes OS |
|---|---|---|
| Code organization | Monolithic prototype | Modular architecture |
| Blink detection | Fixed thresholds and direct loop logic | Stateful engine with calibration and confidence |
| User adaptation | Limited or global settings | Personalized open/closed-eye thresholds |
| Head orientation | Not integrated as a safety gate | Yaw and pitch validation before selection |
| Menu behavior | Fixed menu order | Frequency-based predictive ranking |
| Voice output | Direct prototype implementation | Isolated text-to-speech service |
| Emergency communication | Not available | AWS SNS-compatible simulated notifier |
| Testability | Difficult to isolate components | Independent core, calibration, and interaction boundaries |
| Deployment direction | Desktop experiment | Local-first assistive platform with cloud extension points |

## Project Structure

```text
TalkinEyes/
├── calibration/       # User-specific calibration and profiles
├── cloud/             # Cloud notification boundaries
├── communication/     # Text-to-speech and priority communication
├── core/              # Camera, landmarks, EAR, blinks, and head pose
├── experimental/      # Isolated research experiments
├── intelligence/      # History and predictive ranking
├── interaction/       # Scanning and interaction state boundaries
├── optimization/      # Future benchmarks and model optimization
├── tests/              # Automated test boundaries
├── ui/                 # Tkinter presentation components
├── main.py            # Application composition entry point
└── requirements.txt   # Python dependencies
```

## Installation

### Requirements

- Python 3.11 recommended.
- A working webcam.
- Windows, macOS, or Linux with the required OpenCV and MediaPipe support.

### Setup

Clone or download the repository, open a terminal in the `TalkinEyes`
directory, and install the dependencies:

```bash
pip install -r requirements.txt
```

### Run

```bash
python main.py
```

On first use, run the calibration flow and follow the on-screen instructions.
The generated user profile is stored locally and can be recalibrated when
camera conditions or user needs change.

## Development Status

TalkinEyes OS is an active research and development project. The core local
pipeline is implemented as a functional prototype, while advanced adaptive
interaction, production cloud delivery, optimization, and experimental vision
features are being developed progressively.

AWS notifications are currently simulated. No production credentials are
required or stored in this repository.

## Future Work

The roadmap includes:

- Robust interaction state management and explicit confirmation flows.
- Better handling of camera loss, face loss, and uncertain detections.
- More comprehensive automated tests and real-world benchmark datasets.
- Configurable scan speed, menu size, visual contrast, and voice settings.
- Offline phrase editing, favorites, repetition, and communication history.
- Deterministic contextual prediction before introducing generative AI.
- Production AWS SNS integration with authentication, encryption, and audit
  controls.
- Privacy-preserving telemetry and consent-based diagnostics.
- Performance benchmarking and optional ONNX acceleration.
- Additional signals such as optical flow, eyebrow gestures, and refined gaze
  estimation.

## Responsible Assistive Technology

TalkinEyes OS is intended to assist communication, not replace clinical
assessment or professional assistive-technology guidance. Any deployment in a
care environment should include user testing, caregiver feedback, privacy
review, and an independent emergency-communication fallback.
