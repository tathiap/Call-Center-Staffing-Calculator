# Call Center Staffing Calculator
## Overview
This project implements the Erlang C formula to calculate optimal call center staffing levels. Using real telecom call data from Megaline (137,735 records), it demonstrates workforce capacity planning for customer service operations.

**Business Impact:**  Erlang C enables workforce management teams to:
  * Forecast staffing needs 3-6 months in advance
    
  * Balance service level agreements with labor costs
    
  * Optimize shift schedules based on predicted call patterns
    
  * Make data-driven decisions about service level targets

## Key Findings
Analysis of Megaline Call Data:

* Average Handle Time (AHT): 6.75 minutes
  
* Peak call volume: 392 calls/hour (midnight)
  
* Peak staffing requirement: 73 FTE (80/20 SLA with 30% shrinkage)
  
* Service level trade-off: Moving from 80/20 to 90/30 SLA requires 5-6% additional staff
  
**Insight:** Staffing doesn't scale linearly with volume doubling call volume requires only ~60% more agents, demonstrating economies of scale in call center operations.

## Technical Implementation
### Data Processing
  * Input: 137,735 call records (user_id, call_date, duration)
    
  * Transformation: Aggregated to hourly call volumes with weekday/weekend breakdown
    
  * Output: Hourly averages, handle time statistics, peak period identification
    
### Erlang C Calculator
  * Calculates probability of waiting using traffic intensity (Erlangs)
    
  * Determines minimum agents needed for service level targets (80/20, 90/30)
    
  * Adjusts for shrinkage (breaks, training, absences)
    
  * Compares multiple SLA scenarios for cost-benefit analysis
    
### Visualizations
  * Call Volume Patterns: Hourly distribution and weekday vs. weekend trends
    
  * Staffing Curve: Non-linear relationship between volume and required headcount

## Methodology
### Erlang C Formula:

    Traffic Intensity (A) = (calls_per_hour × AHT_seconds) / 3600
    Service Level = 1 - (P_wait × e^(-(agents - A) × (target_seconds / AHT)))

### Shrinkage Adjustment:

    Required FTE = Required Agents / (1 - Shrinkage%)
    Industry standard shrinkage: 25-35%

### Assumptions:
  * Poisson arrival distribution (random, independent calls)
    
  * Exponential service time distribution
    
  * Infinite queue capacity (no abandoned calls)


## Business Applications

### Capacity Planning
* **Question:** *If call volume increases 20%, how many agents do we need?*

* **Answer:** Use staffing curve to calculate exact headcount. For Megaline peak (392 calls/hour): Current 73 FTE → +20% volume requires 86 FTE (+13 agents)

### Service Level Trade-offs
* **Question:** *What's the cost of improving from 80/20 to 90/30 SLA?*

* **Answer:** 80/20 = 73 FTE | 90/30 = 77 FTE | +4 FTE = 5.5% labor cost increase

### Shift Optimization
* **Question:** *Should we staff the same all day?*

* **Answer:** Peak hours require 73 FTE, off-peak requires significantly less. Flexible scheduling reduces costs vs. flat staffing.


## Technologies
  * Python 3.x: Data processing and analysis
    
  * pandas, numpy: Data manipulation
    
  * scipy: Erlang C mathematical functions
    
  * matplotlib, seaborn: Data visualization
    
  *  Jupyter Notebook: Interactive analysis



## Quick Start
#### Install dependencies:

    bash
    pip install pandas numpy scipy matplotlib seaborn jupyter

#### Process call data:

    bash
    python process_megaline_data.py
    
#### Test calculator:

    bash
    python erlang_c_calculator.py
    
#### Run full analysis:

    bash
    jupyter notebook staffing_analysis.ipynb

### Example Usage
    python
    
    from erlang_c_calculator import calculate_required_agents

    result = calculate_required_agents(
        calls_per_hour=100,
        aht_minutes=5.0,
        target_service_level=80,   # 80% of calls...
        target_seconds=20,          # ...answered within 20 seconds
        shrinkage_pct=0.30          # 30% shrinkage
    )

    print(f"Required agents: {result['required_agents']}")
    print(f"Total FTE: {result['required_fte']}")
    print(f"Service level achieved: {result['service_level']}%")

### Output:
    Required agents: 12
    Total FTE: 18
    Service level achieved: 85.4%

## Data Source
Analysis uses call pattern data from Megaline Telecom:
  * 137,735 call records
  * Date range: January - December 2018
  * Average handle time: 6.75 minutes
  * Hourly volumes ranging from 5-392 calls/hour

## Skills Demonstrated
  * **Workforce Management Mathematics:** Erlang C formula, traffic intensity, service level optimization
  * **Operational Analytics:** Capacity planning, cost-benefit analysis, resource optimization
  * **Python Development:** Modular code design, data processing pipelines, mathematical modeling
  * **Data Visualization:** Business ready charts for stakeholder communication
  * **Domain Translation:** Applying telecom data to call center workforce planning

## Future Enhancements
  * Multi-channel support (email/chat queues)
  * Abandonment modeling (caller patience factors)
  * Real-time dashboard for live staffing vs. demand monitoring
  * Monte Carlo simulation for forecast uncertainty
  * Cost optimization including overtime, part-time, and outsourcing options

## About
**Project Type:** Workforce Management Analytics Portfolio 

**Purpose:** Demonstrate understanding of call center capacity planning and operational mathematics 

**Domain:** Contact Center Operations, Workforce Management

