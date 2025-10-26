import csv
import os
import datetime
from decimal import Decimal
from collections import defaultdict

TRANSACTIONS_FILE = "data/transaction.csv"


def calculate_financial_health_score(savings_ratio):
    """
    Calculate Financial Health Score based on savings ratio
    
    Savings Ratio Ranges:
    < 0%      → Score: 0-25   (Critical - Deficit)
    0-10%     → Score: 25-50  (Weak)
    10-25%    → Score: 50-75  (Good)
    25-40%    → Score: 75-90  (Very Good)
    > 40%     → Score: 90-100 (Excellent)
    """
    if savings_ratio < 0:
        # Deficit scenario: score decreases with larger deficit
        score = 20 + (savings_ratio * 50)
        score = max(0, score)  # Don't go below 0
    elif 0 <= savings_ratio < 0.1:
        # 0-10% savings: score from 25 to 50
        score = 25 + (savings_ratio * 250)
    elif 0.1 <= savings_ratio < 0.25:
        # 10-25% savings: score from 50 to 75
        score = 50 + ((savings_ratio - 0.1) * 167)
    elif 0.25 <= savings_ratio < 0.4:
        # 25-40% savings: score from 75 to 90
        score = 75 + ((savings_ratio - 0.25) * 100)
    else:
        # > 40% savings: score from 90 to 100
        score = 90 + ((savings_ratio - 0.4) * 25)
        score = min(100, score)  # Cap at 100
    
    return round(score, 2)


def categorize_score(score):
    """Categorize the financial health score"""
    if score < 40:
        return "Critical ⚠️"
    elif score < 60:
        return "Weak 📉"
    elif score < 75:
        return "Good 👍"
    elif score < 90:
        return "Very Good 💪"
    else:
        return "Excellent ⭐"


def get_monthly_data(profile_id):
    """
    Get monthly income and expenses data for a profile
    Returns: dict of {month: {'income': amount, 'expenses': amount}}
    """
    if not os.path.exists(TRANSACTIONS_FILE):
        return {}
    
    monthly_data = defaultdict(lambda: {'income': Decimal('0'), 'expenses': Decimal('0')})
    
    with open(TRANSACTIONS_FILE, 'r', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            cleaned = {k.strip(): v.strip() for k, v in row.items()}
            
            if cleaned.get('profile_id') != profile_id:
                continue
            
            try:
                txn_date = datetime.datetime.strptime(cleaned['date'], '%Y-%m-%d')
                month_key = txn_date.strftime('%Y-%m')  # Format: 2025-10
                amount = Decimal(cleaned['amount'])
                
                if cleaned['type'] == 'income':
                    monthly_data[month_key]['income'] += amount
                elif cleaned['type'] == 'expense':
                    monthly_data[month_key]['expenses'] += amount
            except:
                continue
    
    return dict(monthly_data)


def show_financial_health(profile):
    """Display Financial Health Score report"""
    print('\n' + '='*80)
    print(f'💰 Financial Health Score - Profile: {profile["profile_name"]}')
    print('='*80)
    
    monthly_data = get_monthly_data(profile['profile_id'])
    
    if not monthly_data:
        print('\n⚠️  No transaction data found. Please add some transactions first.')
        return
    
    # Sort months chronologically
    sorted_months = sorted(monthly_data.keys())
    
    # Calculate scores for each month
    monthly_scores = []
    
    print(f'\n{"Month":<12} {"Income":<12} {"Expenses":<12} {"Net":<12} {"Ratio":<10} {"Score":<8} {"Status"}')
    print('-' * 80)
    
    for month in sorted_months:
        data = monthly_data[month]
        income = data['income']
        expenses = data['expenses']
        net_balance = income - expenses
        
        # Skip months with no income to avoid division by zero
        if income == 0:
            print(f'{month:<12} {income:<12} {expenses:<12} {net_balance:<12} {"N/A":<10} {"N/A":<8} {"No Income"}')
            continue
        
        savings_ratio = float(net_balance / income)
        score = calculate_financial_health_score(savings_ratio)
        category = categorize_score(score)
        
        monthly_scores.append(score)
        
        # Format output
        ratio_str = f'{savings_ratio:.1%}'
        print(f'{month:<12} {income:<12.2f} {expenses:<12.2f} {net_balance:<12.2f} {ratio_str:<10} {score:<8.2f} {category}')
    
    print('-' * 80)
    
    # Calculate average score
    if monthly_scores:
        avg_score = sum(monthly_scores) / len(monthly_scores)
        avg_category = categorize_score(avg_score)
        
        print(f'\n📊 Summary:')
        print(f'   Total Months Analyzed: {len(monthly_scores)}')
        print(f'   Average Health Score: {avg_score:.2f}/100')
        print(f'   Overall Status: {avg_category}')
        
        # Show trend for last 3 months if available
        if len(monthly_scores) >= 3:
            recent_3_avg = sum(monthly_scores[-3:]) / 3
            print(f'\n📈 Recent Trend (Last 3 Months):')
            print(f'   Average Score: {recent_3_avg:.2f}/100')
            print(f'   Status: {categorize_score(recent_3_avg)}')
            
            # Show if improving or declining
            if len(monthly_scores) >= 6:
                older_3_avg = sum(monthly_scores[-6:-3]) / 3
                if recent_3_avg > older_3_avg:
                    print(f'   Trend: ⬆️ Improving (+{recent_3_avg - older_3_avg:.2f} points)')
                elif recent_3_avg < older_3_avg:
                    print(f'   Trend: ⬇️ Declining ({recent_3_avg - older_3_avg:.2f} points)')
                else:
                    print(f'   Trend: ➡️ Stable')
        

        print(f'\n💡 Recommendations:')
        if avg_score < 40:
            print('   • Your expenses exceed your income. Focus on reducing unnecessary expenses.')
            print('   • Create a strict budget and track all spending.')
            print('   • Look for ways to increase your income.')
        elif avg_score < 60:
            print('   • Try to save at least 10% of your monthly income.')
            print('   • Review your expenses and identify areas to cut back.')
            print('   • Build an emergency fund.')
        elif avg_score < 75:
            print('   • Good progress! Aim to increase savings to 25% of income.')
            print('   • Consider investing your savings for better returns.')
            print('   • Continue tracking expenses carefully.')
        elif avg_score < 90:
            print('   • Excellent financial discipline! Keep it up.')
            print('   • Consider diversifying your investments.')
            print('   • Focus on long-term financial goals.')
        else:
            print('   • Outstanding financial health! You\'re doing great.')
            print('   • Maintain this discipline and consider advanced investment strategies.')
            print('   • Help others learn from your financial habits.')
    
    print('\n' + '='*80)