"""
Erlang C Staffing Calculator

Industry-standard formula for call center capacity planning.
Calculates required agents based on call volume, handle time, and service level targets.
"""

import numpy as np
from scipy.special import factorial
from math import exp


def erlang_c(agents, traffic_intensity):
    """
    Calculate Erlang C probability (probability that a call waits in queue).
    
    Parameters:
    -----------
    agents : int
        Number of agents available
    traffic_intensity : float
        Erlangs (call_rate × average_handle_time / 3600)
    
    Returns:
    --------
    float : Probability of waiting (0-1)
    """
    if agents <= traffic_intensity:
        return 1.0  # Unstable system - calls will queue indefinitely
    
    # Erlang B formula (intermediate step)
    erlang_b_sum = sum([traffic_intensity**k / factorial(k) for k in range(agents)])
    erlang_b = (traffic_intensity**agents / factorial(agents)) / erlang_b_sum
    
    # Erlang C formula
    erlang_c_prob = erlang_b / (1 - (traffic_intensity/agents) * (1 - erlang_b))
    
    return erlang_c_prob


def calculate_service_level(agents, calls_per_hour, aht_seconds, target_seconds):
    """
    Calculate the percentage of calls answered within target time.
    
    Parameters:
    -----------
    agents : int
        Number of agents available
    calls_per_hour : float
        Expected call volume per hour
    aht_seconds : float
        Average handle time in seconds
    target_seconds : float
        Service level target window (e.g., 20 seconds for 80/20)
    
    Returns:
    --------
    float : Service level percentage (0-100)
    """
    # Traffic intensity in Erlangs
    traffic_intensity = (calls_per_hour * aht_seconds) / 3600
    
    if agents <= traffic_intensity:
        return 0.0  # System overloaded
    
    # Probability of waiting
    prob_wait = erlang_c(agents, traffic_intensity)
    
    # Service level calculation (probability answered within target)
    # Formula: SL = 1 - (P_wait × e^(-(agents - traffic) × (target / aht)))
    service_level = 1 - (prob_wait * exp(-(agents - traffic_intensity) * (target_seconds / aht_seconds)))
    
    return service_level * 100  # Return as percentage


def calculate_required_agents(calls_per_hour, aht_minutes, target_service_level, 
                              target_seconds, shrinkage_pct=0.30, max_agents=100):
    """
    Find minimum agents needed to meet service level target.
    
    Parameters:
    -----------
    calls_per_hour : float
        Expected call volume
    aht_minutes : float
        Average handle time in minutes
    target_service_level : float
        Desired service level (e.g., 80 for 80%)
    target_seconds : float
        SL window (e.g., 20 for "within 20 seconds")
    shrinkage_pct : float
        Percentage of time agents unavailable (breaks, training, etc.)
    max_agents : int
        Maximum agents to try (safety limit)
    
    Returns:
    --------
    dict : {
        'required_agents': int,        # Agents needed on phones
        'required_fte': int,            # Total FTE including shrinkage
        'service_level': float,         # Actual SL achieved
        'occupancy': float,             # % time agents busy
        'shrinkage_pct': float,         # Shrinkage percentage used
        'traffic_intensity': float,     # Erlangs
        'calls_per_hour': float,        # Input volume
        'aht_minutes': float            # Input AHT
    }
    """
    aht_seconds = aht_minutes * 60
    traffic_intensity = (calls_per_hour * aht_seconds) / 3600
    
    # Start with minimum theoretical agents (must be > traffic intensity)
    min_agents = int(np.ceil(traffic_intensity)) + 1
    
    # Increment agents until service level is met
    for agents in range(min_agents, max_agents + 1):
        sl = calculate_service_level(agents, calls_per_hour, aht_seconds, target_seconds)
        
        if sl >= target_service_level:
            # Found minimum agents needed
            required_fte = int(np.ceil(agents / (1 - shrinkage_pct)))
            occupancy = (traffic_intensity / agents) * 100
            
            return {
                'required_agents': agents,
                'required_fte': required_fte,
                'service_level': round(sl, 2),
                'occupancy': round(occupancy, 2),
                'shrinkage_pct': shrinkage_pct * 100,
                'traffic_intensity': round(traffic_intensity, 2),
                'calls_per_hour': calls_per_hour,
                'aht_minutes': aht_minutes
            }
    
    # Could not meet service level with max_agents
    return None


def compare_service_levels(calls_per_hour, aht_minutes, shrinkage_pct=0.30):
    """
    Compare staffing requirements for different service level targets.
    
    Common industry standards:
    - 80/20: 80% of calls answered within 20 seconds
    - 90/30: 90% of calls answered within 30 seconds
    
    Returns:
    --------
    dict : Comparison of different SLA configurations
    """
    scenarios = [
        ("80/20", 80, 20),
        ("80/30", 80, 30),
        ("90/20", 90, 20),
        ("90/30", 90, 30)
    ]
    
    results = {}
    
    for name, target_sl, target_sec in scenarios:
        result = calculate_required_agents(
            calls_per_hour, aht_minutes, target_sl, target_sec, shrinkage_pct
        )
        if result:
            results[name] = result
    
    return results


# Example usage and testing
if __name__ == "__main__":
    print("="*70)
    print("ERLANG C STAFFING CALCULATOR - DEMO")
    print("="*70)
    
    # Example scenario
    calls_per_hour = 100
    aht_minutes = 5.0
    target_sl = 80
    target_sec = 20
    shrinkage = 0.30
    
    print(f"\nScenario:")
    print(f"  Call volume: {calls_per_hour} calls/hour")
    print(f"  Average handle time: {aht_minutes} minutes")
    print(f"  Target service level: {target_sl}% in {target_sec} seconds")
    print(f"  Shrinkage: {shrinkage*100}%")
    
    result = calculate_required_agents(calls_per_hour, aht_minutes, target_sl, target_sec, shrinkage)
    
    if result:
        print(f"\n{'='*70}")
        print("RESULTS:")
        print(f"{'='*70}")
        print(f"  Agents needed (on phones): {result['required_agents']}")
        print(f"  Total FTE (with shrinkage): {result['required_fte']}")
        print(f"  Service level achieved: {result['service_level']}%")
        print(f"  Agent occupancy: {result['occupancy']}%")
        print(f"  Traffic intensity: {result['traffic_intensity']} Erlangs")
    else:
        print("\n⚠ Could not meet service level target")
    
    # Compare different SLA targets
    print(f"\n{'='*70}")
    print("SERVICE LEVEL COMPARISON:")
    print(f"{'='*70}")
    
    comparison = compare_service_levels(calls_per_hour, aht_minutes, shrinkage)
    
    print(f"\n{'SLA':<10} {'Agents':<10} {'FTE':<10} {'Actual SL':<12} {'Occupancy'}")
    print("-"*70)
    
    for sla_name, data in comparison.items():
        print(f"{sla_name:<10} {data['required_agents']:<10} {data['required_fte']:<10} "
              f"{data['service_level']:<12.1f} {data['occupancy']:.1f}%")
    
    print("\n" + "="*70)
    print("INTERPRETATION:")
    print("="*70)
    if "90/30" in comparison and "80/20" in comparison:
        diff = comparison["90/30"]["required_fte"] - comparison["80/20"]["required_fte"]
        pct_increase = (diff / comparison["80/20"]["required_fte"]) * 100
        print(f"Moving from 80/20 to 90/30 requires {diff} additional FTE")
        print(f"That's a {pct_increase:.1f}% increase in staffing costs")
    print("="*70)
