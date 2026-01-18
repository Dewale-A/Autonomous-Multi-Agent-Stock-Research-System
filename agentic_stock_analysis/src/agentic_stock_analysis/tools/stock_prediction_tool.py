from crewai.tools import tool
import yfinance as yf
import json
from datetime import datetime
import numpy as np


@tool("stock_prediction")
def stock_prediction(ticker: str, horizon_days: int = 5) -> str:
    """Generate a rules-based directional prediction for a stock."""
    try:
        stock = yf.Ticker(ticker.upper())
        hist = stock.history(period="3mo")
        
        if len(hist) < 50:
            return json.dumps({"ticker": ticker.upper(), "error": "Insufficient data"}, indent=2)
        
        current_price = hist['Close'].iloc[-1]
        sma_20 = hist['Close'].rolling(window=20).mean().iloc[-1]
        sma_50 = hist['Close'].rolling(window=50).mean().iloc[-1]
        
        # RSI calculation
        delta = hist['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        rsi = (100 - (100 / (1 + rs))).iloc[-1]
        
        # Trend signal
        if current_price > sma_20 > sma_50:
            trend = "bullish"
        elif current_price < sma_20 < sma_50:
            trend = "bearish"
        else:
            trend = "mixed"
        
        # Composite score
        score = 0.0
        if trend == "bullish": score += 0.4
        elif trend == "bearish": score -= 0.4
        
        if rsi > 50: score += 0.25 * min((rsi - 50) / 30, 1)
        else: score -= 0.25 * min((50 - rsi) / 30, 1)
        
        momentum_5d = (hist['Close'].iloc[-1] / hist['Close'].iloc[-5] - 1) * 100
        score += 0.2 * np.clip(momentum_5d / 5, -1, 1)
        
        score = np.clip(score, -1, 1)
        
        if score > 0.2:
            direction = "up"
            confidence = min(0.5 + (score * 0.5), 0.85)
        elif score < -0.2:
            direction = "down"
            confidence = min(0.5 + (abs(score) * 0.5), 0.85)
        else:
            direction = "neutral"
            confidence = 0.4 + (0.3 - abs(score)) * 0.3
        
        rationale = f"{'Bullish' if trend == 'bullish' else 'Bearish' if trend == 'bearish' else 'Mixed'} trend ({trend}), RSI {rsi:.0f}, 5-day momentum +{momentum_5d:.1f}%"
        
        return json.dumps({
            "ticker": ticker.upper(),
            "predicted_direction": direction,
            "confidence_score": round(confidence, 3),
            "horizon_days": horizon_days,
            "brief_rationale": rationale,
            "disclaimer": "Model-based signal for informational purposes only."
        }, indent=2)
        
    except Exception as e:
        return json.dumps({"ticker": ticker, "error": str(e)}, indent=2)


@tool("batch_stock_predictions")
def batch_stock_predictions(tickers: str, horizon_days: int = 5) -> str:
    """Generate predictions for multiple stocks (comma-separated)."""
    try:
        ticker_list = [t.strip().upper() for t in tickers.split(",")]
        predictions = []
        
        for ticker in ticker_list[:10]:
            try:
                stock = yf.Ticker(ticker)
                hist = stock.history(period="3mo")
                
                if len(hist) < 50:
                    predictions.append({
                        "ticker": ticker, "predicted_direction": "insufficient_data",
                        "confidence_score": 0, "horizon_days": horizon_days,
                        "brief_rationale": "Insufficient data"
                    })
                    continue
                
                current_price = hist['Close'].iloc[-1]
                sma_20 = hist['Close'].rolling(window=20).mean().iloc[-1]
                sma_50 = hist['Close'].rolling(window=50).mean().iloc[-1]
                
                delta = hist['Close'].diff()
                gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
                loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
                rs = gain / loss
                rsi = (100 - (100 / (1 + rs))).iloc[-1]
                
                if current_price > sma_20 > sma_50: trend = "bullish"
                elif current_price < sma_20 < sma_50: trend = "bearish"
                else: trend = "mixed"
                
                score = 0.0
                if trend == "bullish": score += 0.4
                elif trend == "bearish": score -= 0.4
                if rsi > 50: score += 0.25 * min((rsi - 50) / 30, 1)
                else: score -= 0.25 * min((50 - rsi) / 30, 1)
                
                momentum_5d = (hist['Close'].iloc[-1] / hist['Close'].iloc[-5] - 1) * 100
                score += 0.2 * np.clip(momentum_5d / 5, -1, 1)
                score = np.clip(score, -1, 1)
                
                if score > 0.2:
                    direction = "up"
                    confidence = min(0.5 + (score * 0.5), 0.85)
                elif score < -0.2:
                    direction = "down"
                    confidence = min(0.5 + (abs(score) * 0.5), 0.85)
                else:
                    direction = "neutral"
                    confidence = 0.4 + (0.3 - abs(score)) * 0.3
                
                predictions.append({
                    "ticker": ticker, "predicted_direction": direction,
                    "confidence_score": round(confidence, 3), "horizon_days": horizon_days,
                    "brief_rationale": f"{'Bullish' if trend == 'bullish' else 'Mixed'} signals: trend {trend}, RSI {rsi:.0f}, {'low' if confidence < 0.5 else 'moderate'} conviction"
                })
                
            except Exception as e:
                predictions.append({
                    "ticker": ticker, "predicted_direction": "error",
                    "confidence_score": 0, "horizon_days": horizon_days,
                    "brief_rationale": f"Error: {str(e)}"
                })
        
        return json.dumps(predictions, indent=2)
        
    except Exception as e:
        return json.dumps({"error": str(e)}, indent=2)


@tool("anomaly_detection")
def anomaly_detection(ticker: str) -> str:
    """Detect unusual patterns or anomalies in stock behavior."""
    try:
        stock = yf.Ticker(ticker.upper())
        hist = stock.history(period="3mo")
        
        if len(hist) < 20:
            return json.dumps({"ticker": ticker.upper(), "error": "Insufficient data"}, indent=2)
        
        anomalies = []
        
        avg_volume = hist['Volume'].rolling(window=20).mean()
        volume_std = hist['Volume'].rolling(window=20).std()
        latest_volume = hist['Volume'].iloc[-1]
        latest_avg = avg_volume.iloc[-1]
        
        if latest_avg > 0 and volume_std.iloc[-1] > 0:
            volume_z = (latest_volume - latest_avg) / volume_std.iloc[-1]
            if abs(volume_z) > 2:
                anomalies.append({
                    "type": "volume_spike",
                    "severity": "high" if abs(volume_z) > 3 else "medium",
                    "description": f"Volume is {volume_z:.1f} std devs from average"
                })
        
        returns = hist['Close'].pct_change()
        latest_return = returns.iloc[-1]
        return_std = returns.rolling(window=20).std().iloc[-1]
        
        if return_std > 0:
            return_z = latest_return / return_std
            if abs(return_z) > 2:
                anomalies.append({
                    "type": "price_movement",
                    "severity": "high" if abs(return_z) > 3 else "medium",
                    "description": f"Daily return ({latest_return*100:.2f}%) is {return_z:.1f} std devs from normal"
                })
        
        return json.dumps({
            "ticker": ticker.upper(),
            "anomalies_detected": len(anomalies),
            "anomalies": anomalies,
            "disclaimer": "Anomaly flags are for informational purposes only."
        }, indent=2)
        
    except Exception as e:
        return json.dumps({"ticker": ticker, "error": str(e)}, indent=2)





