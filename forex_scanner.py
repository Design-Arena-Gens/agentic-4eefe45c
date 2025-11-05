#!/usr/bin/env python3
"""
Forex Scanner - Live Currency Exchange Rate Monitor
Fetches real-time exchange rates for multiple currency pairs using Alpha Vantage API
"""

import requests
import time
from datetime import datetime
from typing import Dict, List, Optional
import json


class ForexScanner:
    """Main class for scanning forex exchange rates"""

    BASE_URL = "https://www.alphavantage.co/query"

    def __init__(self, api_key: str):
        """
        Initialize the Forex Scanner

        Args:
            api_key: Your Alpha Vantage API key from alphavantage.co
        """
        self.api_key = api_key
        self.cache = {}

    def get_exchange_rate(self, from_currency: str, to_currency: str) -> Optional[Dict]:
        """
        Get exchange rate for a currency pair

        Args:
            from_currency: Base currency code (e.g., 'USD')
            to_currency: Quote currency code (e.g., 'EUR')

        Returns:
            Dictionary with exchange rate data or None if request fails
        """
        params = {
            'function': 'CURRENCY_EXCHANGE_RATE',
            'from_currency': from_currency.upper(),
            'to_currency': to_currency.upper(),
            'apikey': self.api_key
        }

        try:
            response = requests.get(self.BASE_URL, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()

            # Check for API errors
            if 'Error Message' in data:
                print(f"❌ Error: {data['Error Message']}")
                return None

            if 'Note' in data:
                print(f"⚠️  API Limit: {data['Note']}")
                return None

            if 'Realtime Currency Exchange Rate' not in data:
                print(f"❌ Invalid response for {from_currency}/{to_currency}")
                return None

            rate_data = data['Realtime Currency Exchange Rate']

            return {
                'from': rate_data['1. From_Currency Code'],
                'from_name': rate_data['2. From_Currency Name'],
                'to': rate_data['3. To_Currency Code'],
                'to_name': rate_data['4. To_Currency Name'],
                'rate': float(rate_data['5. Exchange Rate']),
                'last_refreshed': rate_data['6. Last Refreshed'],
                'timezone': rate_data['7. Time Zone'],
                'bid': float(rate_data['8. Bid Price']),
                'ask': float(rate_data['9. Ask Price'])
            }

        except requests.exceptions.RequestException as e:
            print(f"❌ Network error: {e}")
            return None
        except (KeyError, ValueError, json.JSONDecodeError) as e:
            print(f"❌ Data parsing error: {e}")
            return None

    def scan_pairs(self, currency_pairs: List[tuple], delay: float = 12.0) -> Dict:
        """
        Scan multiple currency pairs

        Args:
            currency_pairs: List of tuples with (from_currency, to_currency)
            delay: Delay between API calls in seconds (free tier: 5 calls/min)

        Returns:
            Dictionary with results for all pairs
        """
        results = {}
        total_pairs = len(currency_pairs)

        print(f"\n{'='*70}")
        print(f"🔍 FOREX SCANNER - Starting scan of {total_pairs} currency pairs")
        print(f"{'='*70}\n")

        for idx, (from_curr, to_curr) in enumerate(currency_pairs, 1):
            pair_name = f"{from_curr}/{to_curr}"
            print(f"[{idx}/{total_pairs}] Fetching {pair_name}...", end=' ')

            rate_data = self.get_exchange_rate(from_curr, to_curr)

            if rate_data:
                results[pair_name] = rate_data
                print(f"✓ {rate_data['rate']:.4f}")
            else:
                print(f"✗ Failed")

            # Rate limiting: Wait before next request (except for last pair)
            if idx < total_pairs:
                time.sleep(delay)

        return results

    def display_results(self, results: Dict):
        """
        Display scan results in a formatted table

        Args:
            results: Dictionary of scan results
        """
        if not results:
            print("\n❌ No results to display")
            return

        print(f"\n{'='*70}")
        print(f"📊 FOREX SCANNER RESULTS - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"{'='*70}\n")

        # Header
        print(f"{'PAIR':<15} {'RATE':<12} {'BID':<12} {'ASK':<12} {'UPDATED':<20}")
        print(f"{'-'*70}")

        # Data rows
        for pair_name, data in results.items():
            rate = f"{data['rate']:.5f}"
            bid = f"{data['bid']:.5f}"
            ask = f"{data['ask']:.5f}"
            updated = data['last_refreshed']

            print(f"{pair_name:<15} {rate:<12} {bid:<12} {ask:<12} {updated:<20}")

        print(f"{'='*70}\n")

    def calculate_arbitrage(self, results: Dict):
        """
        Calculate potential arbitrage opportunities (basic triangular arbitrage)

        Args:
            results: Dictionary of scan results
        """
        print("💡 Arbitrage Analysis:")
        print("-" * 70)

        # Look for triangular arbitrage opportunities
        pairs_dict = {pair: data['rate'] for pair, data in results.items()}

        # Example: USD/EUR * EUR/GBP * GBP/USD should equal 1 (or close to it)
        # Simplified check for demonstration
        opportunities = []

        for pair1, rate1 in pairs_dict.items():
            for pair2, rate2 in pairs_dict.items():
                if pair1 != pair2:
                    # Calculate spread
                    spread = abs((rate1 * rate2) - 1.0)
                    if spread > 0.01:  # Threshold for potential opportunity
                        opportunities.append((pair1, pair2, spread))

        if opportunities:
            print("⚠️  Potential opportunities detected (further analysis required):")
            for p1, p2, spread in opportunities[:5]:  # Show top 5
                print(f"  • {p1} × {p2} - Spread: {spread:.4f}")
        else:
            print("✓ No significant arbitrage opportunities detected")

        print()


def main():
    """Main function to run the Forex Scanner"""

    print("""
    ╔══════════════════════════════════════════════════════════════╗
    ║                     FOREX SCANNER v1.0                       ║
    ║              Live Currency Exchange Rate Monitor             ║
    ╚══════════════════════════════════════════════════════════════╝
    """)

    # Get API key from user
    api_key = input("Enter your Alpha Vantage API key: ").strip()

    if not api_key:
        print("❌ Error: API key is required!")
        print("   Get your free API key at: https://www.alphavantage.co/support/#api-key")
        return

    # Initialize scanner
    scanner = ForexScanner(api_key)

    # Define currency pairs to scan
    # Popular major pairs
    currency_pairs = [
        ('USD', 'EUR'),  # US Dollar to Euro
        ('USD', 'GBP'),  # US Dollar to British Pound
        ('USD', 'JPY'),  # US Dollar to Japanese Yen
        ('EUR', 'GBP'),  # Euro to British Pound
        ('GBP', 'JPY'),  # British Pound to Japanese Yen
    ]

    print("\n📋 Currency pairs to scan:")
    for from_curr, to_curr in currency_pairs:
        print(f"   • {from_curr}/{to_curr}")

    print("\n⏳ Note: Free API tier allows 5 calls/minute (12 sec delay between calls)")

    proceed = input("\nProceed with scan? (y/n): ").strip().lower()

    if proceed != 'y':
        print("❌ Scan cancelled")
        return

    # Scan the pairs
    results = scanner.scan_pairs(currency_pairs, delay=12.0)

    # Display results
    scanner.display_results(results)

    # Arbitrage analysis
    if len(results) >= 2:
        scanner.calculate_arbitrage(results)

    print("✅ Scan complete!\n")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Scan interrupted by user")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
