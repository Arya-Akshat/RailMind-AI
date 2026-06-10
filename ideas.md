# Far Away 2026 — All Ideas

> **Participant:** Abhyuday Sharma · **Deadline:** June 14, 2026, 11:59 PM IST
> **Competition:** 10,864 registered teams · Top 100 → Delhi · Top 5 → Tokyo

---

## 1. RailMind — Autonomous Railway Operations Agent Swarm

**Theme:** Agentic & Autonomous Systems × Railways
**Tagline:** *"From detection to resolution — zero human delay"*

### Problem
Indian Railways operates 69,000+ route km with ~13,000 trains daily. When a sensor detects a defect, the response chain is fully manual — a human reads the alert, phones a station, coordinates a maintenance crew, and manually adjusts timetables. This takes hours. In safety-critical scenarios, the delay costs lives.

### Solution
A multi-agent swarm where specialized AI agents autonomously handle the entire incident lifecycle:
- **Sentinel Agent** — ingests sensor feeds, detects anomalies, classifies threats
- **Commander Agent** — triages severity, decides response strategy, escalates to human if critical
- **Dispatcher Agent** — auto-assigns maintenance crews, reserves depot slots, issues work orders
- **Scheduler Agent** — re-routes trains, minimizes network-wide delay
- **Communicator Agent** — notifies passengers, alerts station masters
- **Memory Store** — logs incidents, learns patterns from past events

### Tech Stack
- LangGraph (stateful agent orchestration)
- Claude/GPT API (agent reasoning)
- Python / FastAPI backend
- Next.js dashboard with WebSocket real-time streaming
- ChromaDB (vector store for incident history)
- Python data generators (simulated sensor feeds)

### Demo
Live sensor feed appears on dashboard → Sentinel detects "rail fracture Section 47B" → Commander reasons through severity in visible thought chain → Dispatcher creates work order → Scheduler reroutes 3 trains → Communicator sends alerts. Full resolution in <30 seconds.

### Advantages
- Cross-theme (Agentic + Railways) reduces competition in intersection
- Visible agent reasoning chain is a strong "wow" differentiator
- Pure software — no hardware risk on demo day
- Directly addresses railway safety, a national priority
- Scalable pattern to any transportation network

### Risks
- Simulated data may feel less convincing than real sensor input
- Multi-agent coordination complexity — debugging agent interactions is hard
- Needs polished UI to avoid looking like a terminal demo
- No hardware component (hackathon rewards hardware)

---

## 2. ExamShield — Autonomous Examination Integrity Guardian

**Theme:** Agentic & Autonomous Systems × Examinations
**Tagline:** *"Securing 20 million exam-takers — from paper creation to result declaration"*

### Problem
India conducts 50+ national-level exams annually for 20M+ candidates. Paper leaks in NEET-UG affected millions. Current AI proctoring only monitors the test-taking phase, but 80% of fraud happens before the exam (paper printing, transportation, insider leaks). No system connects pre-exam logistics, during-exam monitoring, and post-exam analysis.

### Solution
A 3-phase autonomous agent system securing the entire exam lifecycle:
- **Vault Agent (Pre-Exam)** — monitors paper generation pipeline, tracks access logs, flags unusual access patterns, encrypts and tracks paper distribution
- **Watchdog Agent (During Exam)** — real-time behavioral analysis, gaze tracking + keystroke dynamics, confidence scoring (not binary flags), human-in-loop for edge cases
- **Detective Agent (Post-Exam)** — cross-center answer pattern analysis, statistical anomaly detection, identifies organized cheating networks
- **Oracle Agent (Orchestrator)** — correlates signals across all 3 phases, escalates with evidence chain, generates audit trail

### Tech Stack
- LangGraph (multi-phase state machine)
- Claude API (reasoning + report generation)
- Python / FastAPI backend
- Next.js dashboard with NetworkX graph visualization
- Statistical analysis (Benford's Law, answer distribution correlation)
- PostgreSQL + ChromaDB

### Demo
Simulate paper leak: Vault detects unauthorized access at 2 AM from unusual IP → During exam: Watchdog notices 47 students answering Q17-Q23 in identical unusual order → Post-exam: Detective correlates pre-exam breach with during-exam anomaly → Oracle produces evidence-backed investigation report.

### Advantages
- Addresses root cause (pre-exam logistics) not just symptoms (proctoring)
- Confidence scoring reduces false positives vs. binary cheater/not-cheater
- Extremely topical — NEET controversy is live in June 2026
- Works for any standardized exam globally
- Investigation dashboard with evidence board is visually compelling

### Risks
- Pre-exam security monitoring requires access to institutional systems that don't exist yet
- Behavioral analysis (gaze, keystroke) needs training data per student
- Scope is very broad — 3-phase system is hard to polish in 6 days
- No hardware component

---

## 3. LogiMind — Autonomous Multi-Modal Logistics Optimizer

**Theme:** Agentic & Autonomous Systems × Logistics & Transit
**Tagline:** *"Your shipment hits a problem. The agent fixes it before you even know."*

### Problem
India's logistics cost is 14-16% of GDP (vs. 8-10% in developed nations). When a shipment gets delayed (weather, traffic, breakdown), a human operator must identify the problem, research alternatives, contact carriers, negotiate rates, update the customer, and adjust downstream schedules. Average resolution: 4-8 hours. Large companies handle 500+ exceptions daily.

### Solution
An autonomous exception resolution engine — a multi-agent system:
- **Radar Agent** — continuously monitors GPS, weather, traffic, port status; detects anomalies
- **Sherlock Agent** — diagnoses root cause (weather? breakdown? congestion?)
- **Navigator Agent** — finds alternative routes, calculates ETA impact, simulates options
- **Negotiator Agent** — compares carrier rates, selects cheapest viable option
- **Executor Agent** — implements solution, updates tracking, notifies stakeholders, adjusts downstream schedules
- Human approval required for costs >₹50,000

### Tech Stack
- LangGraph (stateful exception resolution pipeline)
- Claude API (reasoning + communication drafting)
- Python / FastAPI backend
- Next.js mission control dashboard
- Google Maps API / OpenRouteService
- WebSocket streaming
- PostgreSQL + ChromaDB

### Demo
Dashboard shows 12 active shipments on India map → Radar detects ETA breach on Shipment #S-4071 → Sherlock diagnoses: heavy rainfall on NH-48 → Navigator simulates 3 alternate routes → Negotiator finds Route B saves ₹12,000 → Executor auto-reroutes, updates customer. Resolution: 47 seconds.

### Advantages
- Clear before/after metric (4-8 hours → 47 seconds)
- Live map visualization with moving shipments is visually engaging
- Directly addresses India's logistics cost crisis
- Scalable to any logistics operation globally
- Clean agent separation makes architecture easy to explain

### Risks
- Conceptually similar to FleetMind — differentiation is subtle
- Simulated GPS/weather data may feel artificial
- Real carrier negotiation APIs don't exist — must be mocked
- No hardware component
- Route optimization is a well-trodden space — uniqueness is harder to argue

---

## 4. FleetMind — Autonomous Multi-Agent Fleet Orchestration

**Theme:** Agentic & Autonomous Systems × Logistics & Transit
**Tagline:** *"Vehicles that think, negotiate, and coordinate — without a dispatcher"*

### Problem
Indian logistics costs 14% of GDP (vs. 8% globally). 40% of truck trips run empty. No coordination between vehicles — each driver operates in isolation, leading to massive waste of fuel, time, and capacity.

### Solution
A multi-agent AI system where every vehicle in a fleet is an autonomous agent:
- Each vehicle agent autonomously bids for and swaps delivery assignments based on load, fuel, and proximity
- Agents re-route independently using live map data when disruptions occur
- Agents message each other to coordinate pickups, avoid duplication, share loads at hubs
- Each agent monitors its vehicle health and schedules pit stops
- A Supervisor Agent monitors fleet-level KPIs and intervenes only when local decisions hurt global efficiency
- Every decision is logged with full reasoning chains for auditability

### Tech Stack
- Python + LangGraph/CrewAI (multi-agent orchestration)
- FastAPI + Redis (agent messaging bus) + PostgreSQL
- React + Mapbox GL JS (real-time fleet visualization)
- Reinforcement learning for route optimization
- WebSockets for live dashboard updates

### Demo
Live simulation with 50+ vehicle agents on a real map. Introduce an unexpected road closure → watch agents autonomously re-route, redistribute loads, and negotiate swaps in real-time. Click any agent to see its reasoning chain.

### Advantages
- Truly agentic — agents think, decide, act independently (perfect theme fit)
- Cross-theme (Agentic + Logistics) shows breadth
- Inter-agent negotiation is a genuinely novel demo
- Massive economic impact — even 10% improvement saves ₹1.5 lakh crore annually
- Decentralized architecture is technically impressive

### Risks
- Most complex to build — 50 concurrent agents is engineering-heavy
- Conceptually overlaps with LogiMind
- No hardware component
- Simulation with 50+ agents may be slow or buggy on demo day
- RL-based optimization is hard to train meaningfully in 6 days

---

## 5. ExamShield v2 — Behavioral Biometric Anti-Fraud Examination Platform

**Theme:** Examinations
**Tagline:** *"Your typing rhythm is your identity — unforgeable, unfakeable"*

### Problem
India's examination system is in crisis. NEET 2024 paper leaks, CAT impersonation scandals, mass cheating with Bluetooth devices. Current proctoring (face detection via webcam) is trivially defeated — put a photo in front of the camera.

### Solution
A next-generation exam platform with three interlocking systems:
- **Behavioral Biometric Authentication** — typing rhythm, mouse movement patterns, scroll cadence, interaction timing. Builds a unique "behavioral fingerprint" per student during practice sessions. Continuously verifies identity during exam.
- **Dynamic Question Generation** — LLM generates unique question variants per student from a master bank. Same concept, same difficulty — different numbers/phrasing. No "paper" to leak.
- **Adaptive Fairness Engine** — IRT (Item Response Theory) based adaptive difficulty. Adjusts question difficulty in real-time. More accurate scores with fewer questions, inherently resistant to answer-sharing.

### Tech Stack
- React + WebAssembly (in-browser behavioral analysis — privacy-first)
- Python/FastAPI + PostgreSQL
- Keystroke dynamics + mouse kinematics
- LLM API (Claude/GPT) + custom IRT engine
- WebSockets for live proctoring dashboard
- Scikit-learn/PyTorch for behavioral fingerprint matching

### Demo
Student A takes practice test → system learns behavioral fingerprint → Student A starts exam → green identity verification indicators → Student B sits at same computer → within 30 seconds, system flags anomalous typing patterns → show behavioral signature comparison overlaid.

### Advantages
- Novel approach — behavioral biometrics for exams is genuinely innovative
- Privacy-first — all analysis in-browser via WASM, no facial data stored
- Structurally eliminates paper leaks (dynamic generation)
- Impersonation detection demo is a visceral "wow" moment
- Timely — NEET controversy makes this emotionally resonant

### Risks
- Behavioral model needs enough training data — short practice sessions may not suffice
- Typing rhythm varies with stress, fatigue, unfamiliar keyboards
- Dynamic question generation quality is hard to guarantee across subjects
- IRT engine calibration is mathematically complex
- No agentic loop — doesn't fit the "Agentic Systems" theme

---

## 6. RailGuard — Edge AI Railway Track Health Monitor

**Theme:** Railways
**Tagline:** *"Track intelligence that works offline, on a ₹2,000 sensor node"*

### Problem
Indian Railways operates 68,000+ km of track. Manual inspection by gangmen walking tracks is slow, inconsistent, and dangerous. Track defects (cracks, loose fasteners, gauge variations) cause derailments that kill hundreds annually. Early detection could prevent catastrophic failures.

### Solution
An IoT + Edge AI system that continuously monitors track health:
- **Hardware Module:** ESP32 + ADXL345 accelerometer + MAX4466 microphone + DS18B20 temperature sensor + LoRa/SIM800L communication + solar panel + battery
- **Edge AI (TinyML):** Lightweight neural network runs ON the ESP32. Classifies vibration patterns into: Normal, Crack, Loose Fastener, Foreign Object, Gauge Variation. Works offline.
- **Cloud Dashboard:** Real-time track health heat map across routes, color-coded by health status
- **Predictive Maintenance Engine:** ML model forecasts when a segment will degrade to unsafe levels
- **Alert Cascade:** Critical issues → immediate alert to nearest station master + loco pilot

### Tech Stack
- ESP32 + TensorFlow Lite Micro (TinyML)
- ADXL345 (vibration), MAX4466 (acoustic), DS18B20 (temp)
- LoRa (sensor mesh) or SIM800L (cellular)
- Python/FastAPI + TimescaleDB (time-series)
- React + Leaflet/Mapbox (geographic health map)
- KiCad (PCB design)

### Demo
Place sensor module on table. Tap, vibrate, and strike surface → dashboard updates in real-time, classifying each vibration type. Show track health map with green/yellow/red zones. Trigger "critical alert" → show cascade to station master's phone.

### Advantages
- Hardware + Software — judges explicitly reward tangible prototypes
- Edge AI runs offline on microcontroller — not just cloud API calls
- Life-saving impact — prevents derailments
- PCB design in KiCad satisfies hardware submission requirements
- ~₹1,500-2,000 per node — commercially viable at scale

### Risks
- Training data for real track defects is scarce
- Tapping a table to simulate track faults is unconvincing vs. real rail vibrations
- ESP32 TinyML model accuracy may be low without extensive training
- No agentic reasoning loop — purely reactive sensor system
- Hardware failures on demo day are a real risk

---

## 7. SkyShield — Space Weather Intelligence & Impact Assessment Platform

**Theme:** Space & Aerospace
**Tagline:** *"Protecting India's satellites before the storm hits"*

### Problem
Solar storms can disrupt GPS, kill satellite electronics, degrade communications, and damage power grids. India has 60+ operational satellites (NavIC, GSAT, Chandrayaan, Aditya-L1) but no unified, India-focused platform to assess space weather impact on its space and ground infrastructure.

### Solution
A real-time space weather monitoring and ML-powered impact prediction platform:
- **Data Ingestion** — real-time feeds from NOAA SWPC, NASA DONKI, ESA SSA
- **Solar Flare Predictor** — CNN analyzes solar magnetogram images for flare probability (6-24 hr forecast)
- **Geomagnetic Storm Predictor** — LSTM processes solar wind data to predict Kp/Dst index
- **India Impact Mapper** — maps storm severity to regional GPS accuracy, satellite vulnerability, power grid risk, aviation radiation
- **3D Visualization** — real-time 3D Earth showing magnetosphere, satellite positions, impact zones
- **Alert System** — tiered alerts (Watch → Warning → Alert) with sector-specific recommendations
- **Optional Hardware:** Arduino Nano + HMC5883L magnetometer for local geomagnetic monitoring

### Tech Stack
- Python (NOAA/NASA API clients) + Apache Kafka
- PyTorch (CNN for magnetograms, LSTM for solar wind)
- Three.js + CesiumJS (3D Earth with magnetosphere)
- React + D3.js (dashboard)
- FastAPI + PostgreSQL + Redis
- Arduino Nano + HMC5883L (optional hardware)

### Demo
Stunning 3D Earth with real satellite positions, solar wind particles streaming past magnetosphere. Trigger simulated CME → magnetosphere compresses, satellites turn red/yellow, India's map shows GPS degradation zones and power grid risk.

### Advantages
- Visually stunning — 3D Earth with space weather is breathtaking
- Timely — India's space program is booming (Aditya-L1, Gaganyaan)
- Genuine ML — predicting impacts with neural networks, not just displaying data
- Optional magnetometer hardware adds tangibility
- Unique niche — unlikely any other team does space weather

### Risks
- ML model accuracy for solar prediction is research-grade hard
- Training CNN/LSTM on magnetogram/solar wind data requires curated datasets
- 3D visualization (Three.js + CesiumJS) is time-consuming to build well
- No agentic loop — more of a monitoring dashboard than autonomous system
- Niche audience — judges may not intuitively understand space weather relevance

---

## 8. FreshRoute — Smart Cold Chain Monitoring with Predictive Spoilage AI

**Theme:** Logistics & Transit
**Tagline:** *"Predicts spoilage hours before it happens — and reroutes the truck"*

### Problem
India loses ₹92,000 crore ($11B) worth of food annually due to cold chain failures. 40% of fresh produce spoils before reaching consumers. Small farmers and transporters have zero visibility into temperature conditions during transit.

### Solution
An IoT + Edge AI system that monitors cold chain conditions and predicts spoilage:
- **Hardware Sensor Puck:** ESP32-S3 + SHT31 (temp/humidity, ±0.2°C) + NEO-6M GPS + MQ-135 gas sensor (ethylene detection) + Li-Po battery + 3D-printed case
- **Edge Spoilage Model (TinyML):** Runs on ESP32. Uses temperature history + humidity + ethylene levels to predict remaining shelf life
- **Dynamic Shelf-Life Counter:** Live countdown per shipment ("Tomatoes — 47 hours remaining")
- **Autonomous Re-Routing:** If shelf life drops below threshold, suggests rerouting to nearest market
- **Quality Certificate:** Tamper-proof temperature logs, buyer verifies via QR code
- **Fleet Analytics:** Identifies trucks/routes with most temperature violations

### Tech Stack
- ESP32-S3 + TensorFlow Lite Micro
- SHT31 (temp/humidity), NEO-6M (GPS), MQ-135 (gas)
- BLE (local) + WiFi/MQTT (cloud)
- FastAPI + TimescaleDB + Redis
- React + Mapbox (shipment tracking map)
- KiCad (custom sensor puck PCB)

### Demo
Sensor puck in cooler with tomatoes. Dashboard shows temperature, humidity, ethylene, GPS, live shelf-life countdown (63 hours). Open cooler lid → temperature rises → shelf-life drops in real-time (63→52 hours). System alerts: "Temperature breach. Recommend re-routing to Market B (23 km) instead of Market A (180 km)."

### Advantages
- Tangible hardware demo — sensor puck with live data is compelling
- Massive economic impact — reducing food waste saves billions
- Edge AI on device — not just a cloud sensor reader
- PCB design satisfies hackathon hardware requirements
- Clear business model (SaaS + hardware)
- Emotional resonance — food waste while millions go hungry

### Risks
- MQ-135 gas sensor is imprecise for ethylene detection at low concentrations
- ESP32 TinyML spoilage model needs validated training data
- GPS module draws significant power — battery life may be short
- Cold chain monitoring is a crowded commercial space (Emerson, Sensitech)
- No agentic reasoning loop — reactive monitoring system

---

## 9. RailSentinel — Autonomous Track Fault Detection Agent

**Theme:** Agentic & Autonomous Systems + Railways
**Tagline:** *"An onboard vision + vibration AI agent that predicts track failures before they happen"*

### Problem
India has 68,000 km of track. Manual inspection covers maybe 5% adequately. Most derailments happen on sections that were "scheduled for inspection next month". The cost is human lives and thousands of crore in disruption.

### Solution
A compact agent mountable on any loco or maintenance vehicle, fusing:
- **Dashcam frames** — pothole/crack detection via fine-tuned YOLOv8
- **Accelerometer data** — vibration anomaly detection via LSTM
- **GPS coordinates** — geo-tagging every finding
- The agent autonomously decides critical vs. routine, files geo-tagged reports to a central dashboard, suggests maintenance windows without human intervention
- **Dual-confirmation rule:** flag only when both vision AND vibration anomalies co-occur at the same GPS coordinate within 2 seconds
- Confidence-calibrated output ("87% confident, recommend inspection")
- Feedback loop for inspectors to mark false positives → online learning

### Tech Stack
- YOLOv8 (fine-tuned on track defect dataset)
- LSTM anomaly detection
- Raspberry Pi 5 / Jetson Nano
- FastAPI backend
- React dashboard
- Claude API (agent reasoning layer)

### Demo
Simulated dashcam feed with injected track defects → YOLO detects crack → simultaneously, vibration data shows anomaly at same GPS coordinate → agent reasons through severity → files geo-tagged report → dashboard shows track health map with findings.

### Advantages
- Dual-sensor confirmation (vision + vibration) drastically cuts false positives
- Agentic reasoning layer makes it more than just a detector
- Fits on existing locos — zero new infrastructure cost
- Combines computer vision + time-series ML — shows technical breadth
- Confidence calibration builds operator trust

### Risks
- Fine-tuning YOLOv8 requires labeled track defect images — hard to source in 6 days
- Vibration data is noisy (wheel imbalance, load shifts mimic track faults)
- Requires Raspberry Pi / Jetson hardware on hand
- Dashcam + accelerometer fusion adds hardware complexity
- Real-time inference on Pi may have latency issues

---

## 10. ProctorMind — Behaviour-Based Exam Integrity Without Surveillance Creep

**Theme:** Examinations
**Tagline:** *"Detects collusion patterns from answer distributions, not by watching students"*

### Problem
Every Indian exam — JEE, NEET, UPSC — has a paper leak or impersonation scandal. Existing proctoring tools are privacy nightmares that flag dark-skinned students disproportionately and are trivially defeated by a second phone. They surveil but don't detect the real threat: organised syndicate cheating.

### Solution
A statistical + behavioural analysis platform:
- **During exam:** Track response timing per question — suspiciously fast correct answers on hard questions signal pre-knowledge
- **After exam:** Collusion detection — cosine similarity across answer sheets, cluster students with identical rare wrong answers (statistical fingerprint of copied work)
- **Question-level anomaly detection:** If Q.47 has 95% correct rate but Q.12 has 12%, someone leaked Q.47
- Agent synthesises all signals → assigns integrity risk score per candidate and per question
- Uses Wesolowski's method: compare similarity only after controlling for ability level
- Output is always "warrants investigation", never "is cheating" — human review mandatory

### Tech Stack
- Python (scipy, sklearn)
- Cosine similarity clustering
- IRT (Item Response Theory)
- FastAPI
- PostgreSQL
- D3.js visualisation

### Demo
Load simulated exam data with injected collusion patterns → system detects suspicious clusters → network graph shows connected students across exam centers → question anomaly chart highlights likely leaked questions → agent produces investigation report with confidence scores.

### Advantages
- Zero cameras required — works purely on answer data
- Privacy-safe — no surveillance, no biometric data
- Detects the real threat (organized syndicates) not just individual cheaters
- Statistical methods are well-established and defensible
- Output as "warrants investigation" avoids false accusation liability

### Risks
- Students from same coaching institute may have correlated wrong answers (false flags)
- Requires large exam datasets to demonstrate statistical significance
- No real-time component — analysis is post-hoc
- Narrow scope — may feel like "just statistics" to non-technical judges
- No hardware component, no agentic autonomous loop

---

## 11. LastMile Sync — Multi-Modal Last-Mile Orchestration for Tier 2/3 Cities

**Theme:** Logistics & Transit
**Tagline:** *"Coordinates auto-rickshaws, e-bikes, and walking routes into one live delivery mesh"*

### Problem
In Indian Tier 2/3 cities, last-mile delivery fails completely. No Rapido, no reliable auto, no address system. 30% of e-commerce deliveries are returned undelivered — routing is impossible without formal addresses and drivers won't navigate narrow gullies. 500 million Indians live in addressless areas.

### Solution
An orchestration agent that breaks delivery into micro-segments:
- **Leg 1:** Main road auto-rickshaw
- **Leg 2:** Local e-bike mid-segment
- **Leg 3:** Pedestrian handoff to neighbourhood agent (local shopkeeper as pickup point)
- Uses Plus Codes / what3words for address resolution
- Real-time multi-agent negotiation: drivers bid on segments, matched by proximity + reliability score
- Recipients get WhatsApp-native live tracking — no app install needed
- Shopkeepers earn ₹8-12 per successful pickup with weekly leaderboard and UPI payout
- Reliability score is public-facing; bad performers are delisted

### Tech Stack
- Multi-agent auction system
- Plus Codes / what3words API
- WhatsApp Business API
- OSRM routing engine
- Redis pub/sub
- React Native driver app

### Demo
Create a delivery order to an addressless location → system resolves to Plus Code → auto-rickshaw agent bids on Leg 1 → e-bike agent bids on Leg 2 → shopkeeper assigned as pickup point → recipient gets WhatsApp tracking link → delivery completes through 3 handoffs.

### Advantages
- Solves a deeply real Indian problem — 500M people in addressless areas
- WhatsApp-native tracking requires zero app installs
- Shopkeeper micro-franchise model is a novel incentive design
- Multi-modal handoffs demonstrate agent coordination
- Plus Codes/what3words is an elegant address solution

### Risks
- Shopkeeper model has failed before (Dunzo tried it)
- Core code is mostly CRUD APIs and routing — limited AI/ML depth
- WhatsApp Business API has rate limits and approval requirements
- Multi-modal handoffs add operational complexity that's hard to simulate convincingly
- No hardware component, limited technical depth for judges

---

## 12. SkyFarm Intel — Satellite + Drone Fusion for Smallholder Crop Stress Detection

**Theme:** Space & Aerospace
**Tagline:** *"Detects water stress, pest outbreak, and soil depletion 10 days before visible damage"*

### Problem
India loses ₹50,000 crore annually to crop diseases that were detectable 2 weeks before visible symptoms. Smallholders (avg 1.1 hectare) can't afford field sensors. Satellite imagery is too coarse — Sentinel-2's 10m resolution misses plot-level stress in India's fragmented farmland.

### Solution
A two-tier sensing pipeline:
- **Tier 1 — Coarse weekly scan:** Sentinel-2 NDVI/NDWI analysis flags suspicious zones at village level
- **Tier 2 — Precision response:** Flags trigger a lightweight autonomous drone flight for 0.5m resolution multispectral capture
- ML pipeline fuses both tiers to detect: early-stage water stress (thermal bands), fungal infection (spectral signatures), nitrogen depletion
- Output: actionable advisory in Hindi/regional language via SMS ("Block C, northeast corner: apply X, irrigate Y litres on Thursday")
- **Cloud cover solution:** Sentinel-1 SAR (Synthetic Aperture Radar) penetrates cloud cover for monsoon-season operation. SAR provides soil moisture and canopy structure data.

### Tech Stack
- Sentinel-2 via Copernicus API
- Sentinel-1 SAR for monsoon periods
- ArduPilot drone (multispectral payload)
- U-Net segmentation model
- NDVI / thermal band fusion
- FastAPI + Twilio SMS

### Demo
Load real Sentinel-2 imagery of a farming region → ML model highlights stress zones on map → simulate drone dispatch to flagged zone → show high-resolution multispectral overlay → generate SMS advisory in Hindi for the affected farmer.

### Advantages
- Massive real-world impact — ₹50,000 crore in preventable crop loss
- SAR radar solution for monsoon cloud cover is technically sophisticated
- SMS delivery requires no smartphone — reaches poorest farmers
- Satellite data is freely available (Copernicus)
- Two-tier approach (satellite + drone) shows architectural thinking

### Risks
- Processing SAR data is computationally intensive and complex
- Drone hardware + multispectral payload is expensive and hard to demo
- U-Net model needs labeled training data of crop stress from Indian farms
- Cloud cover solution (SAR) is theoretically sound but hard to implement in 6 days
- Agriculture is not an official hackathon theme — must fit under "Space & Aerospace"

---

## 13. StationFlow — Autonomous Crowd & Platform Management Agent

**Theme:** Railways + Agentic & Autonomous Systems
**Tagline:** *"Prevents stampedes by predicting and redistributing crowd density in real time"*

### Problem
The Maha Kumbh 2025 tragedy. The Mumbai CSMT crush in 2017. Indian stations are architecturally not built for current load. Platform allocation is static, done hours before a train arrives. When a train is 40 minutes late, 4,000 people stand on a platform built for 800 — station staff have no data.

### Solution
An autonomous platform management agent:
- **CCTV feed** — density estimation via CSRNet / crowd counting CNN (density maps only, no facial recognition)
- **PRS ticket data** — who booked for which train, on which platform
- **Live train running status** via NTES API
- Agent predicts crowd hotspots 15 minutes ahead and autonomously:
  1. Sends gate-opening/closing instructions to staff via earpiece app
  2. Triggers PA announcements directing passengers to alternate platforms
  3. Alerts RPF when density crosses safe threshold
- **Ground truth calibration:** UHF gate counters (~₹3,000 per entry point)
- **Unreserved passenger proxy:** Mobile network density data (Jio/Airtel anonymised footfall APIs)

### Tech Stack
- CSRNet crowd counting model
- RTSP CCTV stream processing
- PRS API integration
- Railway NTES API
- WebSocket real-time dashboard
- Claude API (autonomous decision layer)

### Demo
Dashboard shows station layout with live density heat map → train delay announced → model predicts crowd buildup on Platform 3 → agent triggers PA announcement to redirect to Platform 5 → gate counters confirm redistribution → density normalizes.

### Advantages
- Life-saving impact — directly prevents stampedes and crushes
- Privacy-safe — density maps only, no facial recognition
- Cross-theme (Railways + Agentic) reduces competition
- Multiple data sources (CCTV + PRS + NTES) shows data fusion sophistication
- 15-minute prediction horizon is a compelling autonomous capability

### Risks
- Indian station CCTV quality is terrible — low resolution, poor lighting, wrong angles
- CSRNet accuracy drops to ~60% in real station conditions
- PRS data misses unreserved passengers (majority on most routes)
- Mobile network density APIs may not be accessible for a hackathon
- Requires simulated CCTV feeds — hard to make convincing
