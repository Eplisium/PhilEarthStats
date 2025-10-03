"""
AI Prompt Management and Optimization (Phase 4.2)
Centralized prompt templates with versioning and model-specific optimizations
"""

# Prompt version for tracking improvements
PROMPT_VERSION = "2.0.0"

# Base system prompts by model type
SYSTEM_PROMPTS = {
    'default': """You are an expert seismologist with deep knowledge of earthquake patterns, tectonic activity, and disaster preparedness in the Philippines region. Provide thorough, accurate, and actionable analysis.""",
    
    'grok': """You are an expert seismologist analyzing Philippine earthquakes. Provide clear, data-driven insights with appropriate technical detail and actionable recommendations.""",
    
    'gpt': """You are a senior seismologist specializing in the Philippine region. Analyze seismic data comprehensively, considering tectonic context, historical patterns, and public safety implications.""",
    
    'gemini': """As a seismology expert focused on Philippine earthquakes, provide comprehensive analysis that balances technical accuracy with accessibility for emergency responders and the public."""
}

def get_system_prompt(model_id):
    """Get appropriate system prompt based on model"""
    if 'grok' in model_id.lower():
        return SYSTEM_PROMPTS['grok']
    elif 'gpt' in model_id.lower():
        return SYSTEM_PROMPTS['gpt']
    elif 'gemini' in model_id.lower():
        return SYSTEM_PROMPTS['gemini']
    return SYSTEM_PROMPTS['default']

def format_energy(joules):
    """Format energy values for display in prompts"""
    if joules >= 1e15:
        return f"{joules/1e15:.2f} × 10¹⁵ joules"
    elif joules >= 1e12:
        return f"{joules/1e12:.2f} × 10¹² joules"
    elif joules >= 1e9:
        return f"{joules/1e9:.2f} × 10⁹ joules"
    else:
        return f"{joules:.2e} joules"

def build_analysis_prompt(stats, regional_stats, historical_comparison, 
                          significant_earthquakes, clusters, sequences, 
                          risk_scores, trends, b_value, volcano_correlation,
                          detail_level='comprehensive'):
    """
    Build optimized analysis prompt with configurable detail level
    
    Args:
        detail_level: 'brief' (500 words), 'standard' (1500 words), 'comprehensive' (2500+ words)
    """
    
    # Detail level configurations
    detail_configs = {
        'brief': {
            'max_clusters': 3,
            'max_sequences': 2,
            'max_earthquakes': 5,
            'sections': ['Executive Summary', 'Key Findings', 'Immediate Recommendations']
        },
        'standard': {
            'max_clusters': 5,
            'max_sequences': 3,
            'max_earthquakes': 8,
            'sections': ['Executive Summary', 'Activity Overview', 'Regional Analysis', 
                        'Risk Assessment', 'Recommendations']
        },
        'comprehensive': {
            'max_clusters': 10,
            'max_sequences': 5,
            'max_earthquakes': 10,
            'sections': ['Executive Summary', 'Seismic Activity Overview', 'Regional Analysis',
                        'Advanced Pattern Recognition', 'Temporal Trends', 'Depth and Energy Analysis',
                        'Statistical Insights', 'Volcano-Earthquake Relationships',
                        'Risk Assessment by Region', 'Recommendations']
        }
    }
    
    config = detail_configs.get(detail_level, detail_configs['comprehensive'])
    
    prompt = f"""You are a seismologist analyzing earthquake data for the Philippines region. Provide a {'brief' if detail_level == 'brief' else 'detailed' if detail_level == 'standard' else 'comprehensive'} analysis based on the following data:

**Analysis Period**: Last {stats.get('period_days', 90)} days

**Overall Statistics**:
- Total earthquakes: {stats['total_count']}
- Average magnitude: M {stats['avg_magnitude']:.2f}
- Maximum magnitude: M {stats['max_magnitude']:.2f}
- Significant events (M ≥ 4.5): {stats['significant_count']}
- Total seismic energy: {format_energy(stats['total_energy_joules'])}
- Average daily energy: {format_energy(stats['avg_daily_energy'])}

**Enhanced Depth Distribution**:
- Very Shallow (< 10 km): {stats['very_shallow_count']} - High damage potential
- Shallow (10-70 km): {stats['shallow_count']} - Moderate damage potential
- Intermediate (70-300 km): {stats['intermediate_count']} - Lower surface impact
- Deep (≥ 300 km): {stats['deep_count']} - Minimal surface impact

**Regional Breakdown**:
"""
    
    # Add regional data
    for region in ['Luzon', 'Visayas', 'Mindanao']:
        r_stats = regional_stats.get(region, {})
        prompt += f"""
**{region}**: {r_stats.get('count', 0)} events ({r_stats.get('percentage', 0)}%), Avg M{r_stats.get('avg_magnitude', 0):.2f}, Max M{r_stats.get('max_magnitude', 0):.1f}, {r_stats.get('significant_count', 0)} significant
"""
    
    # Add historical comparison if available
    if historical_comparison and 'vs_previous_period' in historical_comparison:
        prev = historical_comparison['vs_previous_period']
        prompt += f"""
**Historical Comparison**:
- vs Previous Period: {prev['count_change_percent']:+.1f}% events, {prev['magnitude_change']:+.2f} magnitude change
"""
    
    # Add Phase 2 analytics
    prompt += f"""
**Advanced Analytics**:
- Seismic Clusters: {len(clusters)} detected
- Aftershock Sequences: {len(sequences)} identified
"""
    
    # Add risk scores
    if risk_scores:
        prompt += "\n**Regional Risk Scores (0-100)**:\n"
        for region, risk in risk_scores.items():
            prompt += f"- {region}: {risk['score']} ({risk['level']})\n"
    
    # Add trends
    if trends:
        prompt += f"\n**Trend**: {trends.get('overall_trend', 'Stable')}\n"
    
    # Add b-value if available
    if b_value:
        prompt += f"\n**Gutenberg-Richter b-value**: {b_value}\n"
    
    # Add top earthquakes
    prompt += f"\n**Top {min(config['max_earthquakes'], len(significant_earthquakes))} Significant Earthquakes**:\n"
    for i, eq in enumerate(significant_earthquakes[:config['max_earthquakes']], 1):
        prompt += f"{i}. M{eq['magnitude']:.1f} - {eq['region']} - {eq['place']} - Depth: {eq['depth']:.1f}km\n"
    
    # Add formatting requirements based on detail level
    if detail_level == 'brief':
        prompt += """
Provide a BRIEF analysis (400-600 words) covering:
1. **Executive Summary** (2-3 sentences with key alerts)
2. **Key Findings** (3-4 critical observations)
3. **Immediate Recommendations** (3-5 actionable items)

Keep it concise and focused on immediate concerns.
"""
    elif detail_level == 'standard':
        prompt += """
Provide a STANDARD analysis (1200-1800 words) covering:
1. **Executive Summary**
2. **Activity Overview**
3. **Regional Analysis**
4. **Risk Assessment**
5. **Recommendations**

Balance technical detail with readability.
"""
    else:  # comprehensive
        prompt += f"""
Based on this comprehensive {stats.get('period_days', 90)}-day dataset with advanced analytics, provide a DETAILED, STRUCTURED analysis covering:

## Executive Summary
Provide a concise overview (3-4 sentences) with the most critical findings and overall risk level.

## Seismic Activity Overview
Assess whether current activity is normal, elevated, or concerning compared to historical baselines.

## Regional Analysis
Compare seismic patterns across Luzon, Visayas, and Mindanao. Discuss the risk scores and what they mean for each region.

## Advanced Pattern Recognition
Analyze the detected clusters and aftershock sequences. What do these patterns tell us about ongoing seismic processes?

## Temporal Trends
Examine the trend analysis. Are we seeing increasing, decreasing, or stable activity? What might this indicate?

## Depth and Energy Analysis
Discuss depth distributions and energy release patterns. Are shallow, high-damage-potential earthquakes a concern?

## Statistical Insights
Interpret the b-value (if available). What does it tell us about the stress state in the region?

## Volcano-Earthquake Relationships
Analyze seismic activity near volcanoes. Are there any concerning correlations?

## Risk Assessment by Region
Provide detailed risk assessments for Luzon, Visayas, and Mindanao based on all available data.

## Recommendations
Provide specific, actionable recommendations for:
- Residents in each region
- Local authorities and emergency services
- Monitoring and preparedness efforts
"""
    
    # Universal formatting requirements
    prompt += """
**FORMATTING REQUIREMENTS - CRITICAL**:
- Use proper markdown formatting throughout
- Start main sections with ## (h2 headings)
- Use ### (h3 headings) for subsections
- Use **bold** for emphasis on key terms
- Use bullet points (- ) for lists, NOT asterisks
- Use numbered lists (1. 2. 3.) for sequential information
- Ensure blank lines between paragraphs and sections
- Use single backticks `like this` for inline technical terms, magnitude values
- NEVER use code blocks (```) for magnitude values - only single backticks `
- Use > for important warnings as blockquotes
- Do NOT use unicode symbols like •, ×, ÷
- Write in a clear, professional tone suitable for public safety information
- Start your response immediately with content, no meta-text

Your response will be rendered with ReactMarkdown, so proper markdown syntax is essential.
"""
    
    return prompt

def get_prompt_config(model_id, detail_level='comprehensive'):
    """Get prompt configuration including temperature and max tokens based on model and detail level"""
    
    # Base configurations
    base_config = {
        'temperature': 0.7,
        'max_tokens': 3000
    }
    
    # Adjust for detail level
    if detail_level == 'brief':
        base_config['max_tokens'] = 1000
        base_config['temperature'] = 0.6  # More focused
    elif detail_level == 'standard':
        base_config['max_tokens'] = 2000
        base_config['temperature'] = 0.7
    else:  # comprehensive
        base_config['max_tokens'] = 4000
        base_config['temperature'] = 0.7
    
    # Model-specific adjustments
    if 'grok' in model_id.lower():
        base_config['temperature'] = 0.65  # Grok tends to be verbose
    elif 'gpt-5' in model_id.lower():
        base_config['max_tokens'] = min(base_config['max_tokens'] + 1000, 4000)  # GPT-5 handles longer context well
    
    return base_config

# Prompt templates for different use cases
PROMPT_TEMPLATES = {
    'quick_update': {
        'system': 'Provide a brief earthquake activity update focusing on changes and alerts.',
        'detail_level': 'brief',
        'temperature': 0.6,
        'max_tokens': 800
    },
    'daily_briefing': {
        'system': 'Provide a daily earthquake briefing for emergency response teams.',
        'detail_level': 'standard',
        'temperature': 0.7,
        'max_tokens': 2000
    },
    'scientific_report': {
        'system': 'Provide a comprehensive scientific analysis of seismic activity.',
        'detail_level': 'comprehensive',
        'temperature': 0.8,
        'max_tokens': 4000
    }
}

def get_template_config(template_name='scientific_report'):
    """Get predefined template configuration"""
    return PROMPT_TEMPLATES.get(template_name, PROMPT_TEMPLATES['scientific_report'])
