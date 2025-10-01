# AI Analysis Setup Guide

## Overview
The PhilEarthStats application now includes an AI-powered seismic analysis feature using OpenRouter. This feature provides comprehensive insights from an AI seismologist analyzing the last 30 days of earthquake data for the Philippines region.

## Setup Instructions

### 1. Get Your OpenRouter API Key

1. Visit [OpenRouter](https://openrouter.ai/keys)
2. Sign up or log in
3. Generate a new API key
4. Copy the API key

### 2. Configure Backend

1. Navigate to the `backend` directory
2. Create a `.env` file based on `.env.example`:
   ```bash
   cp .env.example .env
   ```
3. Open `.env` and add your OpenRouter API key:
   ```
   OPENROUTER_API_KEY=your_actual_api_key_here
   ```

### 3. Install Dependencies

#### Backend:
```bash
cd backend
pip install -r requirements.txt
```

#### Frontend:
```bash
cd frontend
npm install
```

### 4. Start the Application

#### Backend:
```bash
cd backend
python app.py
```

#### Frontend:
```bash
cd frontend
npm run dev
```

## Using the AI Analysis Feature

1. Open the application in your browser (typically `http://localhost:3000`)
2. Navigate to the **"AI Analysis"** tab
3. Click the **"Generate AI Analysis"** button
4. Wait 10-30 seconds for the AI to analyze the data
5. View the comprehensive analysis including:
   - Overall seismic activity assessment
   - Pattern and trend analysis
   - Geographic distribution insights
   - Risk assessment
   - Actionable recommendations
   - Notable earthquake sequences

## Features Included

### Backend (`/api/ai/analyze`)
- Fetches 30 days of earthquake data
- Calculates comprehensive statistics
- Prepares detailed prompt for LLM
- Uses Claude 3.5 Sonnet via OpenRouter
- Returns formatted analysis with metadata

### Frontend (AI Analysis Tab)
- Convenient one-click analysis generation
- Beautiful, modern UI with purple/blue gradient theme
- Loading states with progress indicators
- Error handling with helpful messages
- Markdown rendering for formatted analysis
- Statistics cards showing key metrics
- Notable earthquakes list
- Metadata and disclaimers

## Model Selection

The default model is `anthropic/claude-3.5-sonnet`. You can change this in `backend/app.py` on line 614:

```python
model="anthropic/claude-3.5-sonnet",  # Change to other OpenRouter models
```

Popular alternatives:
- `openai/gpt-4-turbo`
- `google/gemini-pro`
- `meta-llama/llama-3.1-70b-instruct`
- See [OpenRouter Models](https://openrouter.ai/models) for full list

## Cost Considerations

- OpenRouter charges per token used
- Claude 3.5 Sonnet: ~$3 per million input tokens, ~$15 per million output tokens
- Each analysis typically uses ~2,000-3,000 tokens total
- Estimated cost per analysis: $0.01-0.05
- Monitor your usage at [OpenRouter Dashboard](https://openrouter.ai/activity)

## Troubleshooting

### "OpenRouter API key not configured" Error
- Ensure `.env` file exists in backend directory
- Verify `OPENROUTER_API_KEY` is set correctly
- Restart the backend server after updating `.env`

### Analysis Takes Too Long
- Normal wait time is 10-30 seconds
- Check your internet connection
- Verify OpenRouter service status
- Consider switching to a faster model

### Invalid API Key Error
- Double-check your API key from OpenRouter dashboard
- Ensure no extra spaces in the `.env` file
- Generate a new key if needed

## Security Notes

- **Never commit your `.env` file to version control**
- Keep your API key confidential
- Use environment variables in production
- Monitor API usage regularly
- Set spending limits on OpenRouter

## Data Privacy

- All earthquake data comes from public USGS API
- No personal data is sent to OpenRouter
- Only seismic statistics and earthquake locations are included in prompts
- See OpenRouter's [Privacy Policy](https://openrouter.ai/privacy)

## Limitations

- Analysis is AI-generated and should be supplementary
- Always refer to official sources (PHIVOLCS) for authoritative information
- LLM responses may vary between analyses
- Analysis limited to last 30 days of data

## Support

For issues or questions:
- Check OpenRouter documentation: https://openrouter.ai/docs
- Review USGS API documentation: https://earthquake.usgs.gov/fdsnws/event/1/
- Contact PHIVOLCS for official earthquake information: https://www.phivolcs.dost.gov.ph/
