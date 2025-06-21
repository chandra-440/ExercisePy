import requests
import pandas as pd
import yfinance as yf
from datetime import datetime, timedelta

# Configuration
FMP_API_KEY = 'your_fmp_api_key_here'  # Get a free API key from https://financialmodelingprep.com/developer/
SELECTED_STOCKS = ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'META']  # Add your selected stocks here

def get_fundamental_data(ticker, api_key, statement_type, period='annual', limit=3):
    """
    Get fundamental data from FinancialModelingPrep API
    """
    base_url = f"https://financialmodelingprep.com/api/v3/{statement_type}/{ticker}"
    params = {
        'apikey': api_key,
        'period': period,
        'limit': limit
    }
    
    try:
        response = requests.get(base_url, params=params)
        response.raise_for_status()
        data = response.json()
        
        if isinstance(data, list):
            return pd.DataFrame(data)
        else:
            print(f"Unexpected response format for {ticker} {statement_type}")
            return pd.DataFrame()
            
    except requests.exceptions.RequestException as e:
        print(f"Error fetching {statement_type} for {ticker}: {e}")
        return pd.DataFrame()

def get_all_fundamentals(ticker, api_key):
    """
    Get all fundamental statements for a given ticker
    """
    print(f"\nFetching fundamental data for {ticker}...")
    
    # Get income statements
    income_statements = get_fundamental_data(ticker, api_key, 'income-statement')
    if not income_statements.empty:
        income_statements['statement'] = 'Income Statement'
    
    # Get balance sheets
    balance_sheets = get_fundamental_data(ticker, api_key, 'balance-sheet-statement')
    if not balance_sheets.empty:
        balance_sheets['statement'] = 'Balance Sheet'
    
    # Get cash flow statements
    cash_flows = get_fundamental_data(ticker, api_key, 'cash-flow-statement')
    if not cash_flows.empty:
        cash_flows['statement'] = 'Cash Flow'
    
    # Combine all statements
    all_statements = pd.concat([income_statements, balance_sheets, cash_flows], ignore_index=True)
    
    return all_statements

def get_market_data(ticker):
    """
    Get current market data using yfinance
    """
    try:
        stock = yf.Ticker(ticker)
        info = stock.info
        
        market_data = {
            'currentPrice': info.get('currentPrice', None),
            'marketCap': info.get('marketCap', None),
            'peRatio': info.get('trailingPE', None),
            'pbRatio': info.get('priceToBook', None),
            'dividendYield': info.get('dividendYield', None),
            '52WeekHigh': info.get('fiftyTwoWeekHigh', None),
            '52WeekLow': info.get('fiftyTwoWeekLow', None)
        }
        
        return pd.DataFrame([market_data])
    except Exception as e:
        print(f"Error fetching market data for {ticker}: {e}")
        return pd.DataFrame()

def analyze_fundamentals(ticker, fundamental_data, market_data):
    """
    Perform basic fundamental analysis
    """
    analysis = {}
    
    # Extract latest year data
    latest_data = fundamental_data[fundamental_data['date'] == fundamental_data['date'].max()]
    
    # Liquidity Ratios
    if not latest_data.empty:
        current_ratio = latest_data['totalCurrentAssets'].values[0] / latest_data['totalCurrentLiabilities'].values[0]
        analysis['Current Ratio'] = current_ratio
    
    # Profitability Ratios (from income statement)
    income_data = fundamental_data[fundamental_data['statement'] == 'Income Statement']
    if not income_data.empty:
        latest_income = income_data[income_data['date'] == income_data['date'].max()]
        if not latest_income.empty:
            gross_margin = latest_income['grossProfit'].values[0] / latest_income['revenue'].values[0]
            net_margin = latest_income['netIncome'].values[0] / latest_income['revenue'].values[0]
            analysis['Gross Margin'] = gross_margin
            analysis['Net Margin'] = net_margin
    
    # Market-based ratios
    if not market_data.empty:
        analysis['P/E Ratio'] = market_data['peRatio'].values[0]
        analysis['P/B Ratio'] = market_data['pbRatio'].values[0]
        analysis['Dividend Yield'] = market_data['dividendYield'].values[0]
    
    return analysis

def main():
    all_data = {}
    
    for ticker in SELECTED_STOCKS:
        # Get fundamental data
        fundamental_data = get_all_fundamentals(ticker, FMP_API_KEY)
        
        # Get market data
        market_data = get_market_data(ticker)
        
        # Perform analysis
        if not fundamental_data.empty:
            analysis = analyze_fundamentals(ticker, fundamental_data, market_data)
            
            # Store data
            all_data[ticker] = {
                'fundamental_data': fundamental_data,
                'market_data': market_data,
                'analysis': analysis
            }
    
    # Display results
    for ticker, data in all_data.items():
        print(f"\n=== {ticker} Fundamental Analysis ===")
        print("\nLast 3 Statements Dates:")
        print(data['fundamental_data']['date'].unique())
        
        print("\nKey Financial Ratios:")
        for ratio, value in data['analysis'].items():
            print(f"{ratio}: {value:.2f}")
        
        print("\nMarket Data:")
        print(data['market_data'].transpose())
    
    return all_data

if __name__ == "__main__":
    fundamental_analysis_data = main()
