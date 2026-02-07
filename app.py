import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime
import matplotlib

# Configure matplotlib to use a non-interactive backend
matplotlib.use('Agg')

# Set page configuration
st.set_page_config(
    page_title="FIRE Journey Planner - Financial Independence Calculator",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        background: linear-gradient(90deg, #2E7D32, #4CAF50);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 700;
        margin-bottom: 1rem;
    }
    .success-box {
        background: linear-gradient(135deg, #E8F5E9, #C8E6C9);
        padding: 2rem;
        border-radius: 10px;
        border-left: 5px solid #4CAF50;
        margin: 1rem 0;
    }
    .info-box {
        background: linear-gradient(135deg, #E3F2FD, #BBDEFB);
        padding: 1.5rem;
        border-radius: 10px;
        border-left: 5px solid #2196F3;
        margin: 1rem 0;
    }
    .warning-box {
        background: linear-gradient(135deg, #FFF3E0, #FFE0B2);
        padding: 1rem;
        border-radius: 10px;
        border-left: 5px solid #FF9800;
        margin: 1rem 0;
    }
    .metric-card {
        background: white;
        padding: 1rem;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        border: 1px solid #E0E0E0;
    }
    .stProgress > div > div > div > div {
        background: linear-gradient(90deg, #4CAF50, #8BC34A);
    }
    .stButton > button {
        width: 100%;
        background: linear-gradient(90deg, #2E7D32, #4CAF50);
        color: white;
        font-weight: bold;
        border: none;
        padding: 0.75rem;
        border-radius: 5px;
    }
    .stButton > button:hover {
        background: linear-gradient(90deg, #1B5E20, #2E7D32);
        color: white;
    }
    h1, h2, h3 {
        color: #1B5E20;
    }
</style>
""", unsafe_allow_html=True)

# Currency conversion rates (hardcoded approximate rates)
CURRENCY_RATES = {
    'USD': 1.0,
    'EUR': 0.92,
    'GBP': 0.79,
    'JPY': 147.50,
    'CAD': 1.35,
    'AUD': 1.52,
    'CHF': 0.88,
    'CNY': 7.18,
    'INR': 83.20,
    'PKR': 277.0,
    'BRL': 4.92,
    'MXN': 17.30,
    'ZAR': 18.65,
    'SGD': 1.34,
    'NZD': 1.63
}

CURRENCY_SYMBOLS = {
    'USD': '$',
    'EUR': '€',
    'GBP': '£',
    'JPY': '¥',
    'CAD': 'CA$',
    'AUD': 'A$',
    'CHF': 'CHF',
    'CNY': '¥',
    'INR': '₹',
    'PKR': '₨',
    'BRL': 'R$',
    'MXN': '$',
    'ZAR': 'R',
    'SGD': 'S$',
    'NZD': 'NZ$'
}

class FIREPlanner:
    def __init__(self):
        self.results = None
        
    def calculate_fire(self, params):
        """Calculate FIRE projections based on user inputs"""
        try:
            # Extract parameters
            current_age = params['current_age']
            retirement_age = params['retirement_age']
            annual_expenses = params['annual_expenses']
            current_net_worth = params['current_net_worth']
            monthly_savings = params['monthly_savings']
            annual_return = params['annual_return'] / 100
            inflation = params['inflation'] / 100
            withdrawal_rate = params['withdrawal_rate'] / 100
            
            # Calculate years until retirement
            years_to_retirement = max(0, retirement_age - current_age)
            
            # Calculate FIRE number (target net worth)
            # Adjust expenses for inflation until retirement
            inflated_expenses = annual_expenses * ((1 + inflation) ** years_to_retirement)
            fire_number = inflated_expenses / withdrawal_rate
            
            # Calculate annual savings
            annual_savings = monthly_savings * 12
            
            # Create year-by-year projection
            projections = []
            net_worth = current_net_worth
            
            for year in range(years_to_retirement + 1):
                age = current_age + year
                
                # Calculate expenses for this year (with inflation)
                current_expenses = annual_expenses * ((1 + inflation) ** year)
                
                # Calculate investment return
                investment_return = net_worth * annual_return
                
                # Add savings for the year (except in retirement year)
                if year < years_to_retirement:
                    net_worth += annual_savings + investment_return
                else:
                    net_worth += investment_return
                
                projections.append({
                    'Year': year,
                    'Age': age,
                    'Net Worth': net_worth,
                    'Annual Savings': annual_savings if year < years_to_retirement else 0,
                    'Investment Return': investment_return,
                    'Annual Expenses': current_expenses,
                    'FIRE Target': fire_number
                })
            
            # Calculate required savings rate to reach FIRE
            if years_to_retirement > 0:
                # Future value calculation for required savings
                future_value_needed = fire_number - current_net_worth * ((1 + annual_return) ** years_to_retirement)
                if future_value_needed > 0:
                    # Calculate required annual savings using future value of annuity formula
                    # FV = P * (((1 + r)^n - 1) / r)
                    # P = FV * (r / ((1 + r)^n - 1))
                    r = annual_return
                    n = years_to_retirement
                    required_annual_savings = future_value_needed * (r / ((1 + r) ** n - 1))
                    required_monthly_savings = required_annual_savings / 12
                else:
                    required_annual_savings = 0
                    required_monthly_savings = 0
            else:
                required_annual_savings = 0
                required_monthly_savings = 0
            
            # Calculate optimistic/pessimistic scenarios
            optimistic_return = annual_return * 1.25  # 25% better returns
            pessimistic_return = max(0.01, annual_return * 0.75)  # 25% worse returns, minimum 1%
            
            optimistic_projection = []
            pessimistic_projection = []
            opt_net_worth = current_net_worth
            pess_net_worth = current_net_worth
            
            for year in range(years_to_retirement + 1):
                if year < years_to_retirement:
                    opt_net_worth += annual_savings + (opt_net_worth * optimistic_return)
                    pess_net_worth += annual_savings + (pess_net_worth * pessimistic_return)
                else:
                    opt_net_worth += opt_net_worth * optimistic_return
                    pess_net_worth += pess_net_worth * pessimistic_return
                
                optimistic_projection.append(opt_net_worth)
                pessimistic_projection.append(pess_net_worth)
            
            self.results = {
                'projections': projections,
                'fire_number': fire_number,
                'years_to_retirement': years_to_retirement,
                'required_annual_savings': required_annual_savings,
                'required_monthly_savings': required_monthly_savings,
                'current_annual_savings': annual_savings,
                'optimistic_projection': optimistic_projection,
                'pessimistic_projection': pessimistic_projection,
                'last_year_net_worth': projections[-1]['Net Worth'] if projections else 0
            }
            
            return True
            
        except Exception as e:
            st.error(f"Calculation error: {str(e)}")
            return False
    
    def format_currency(self, amount, currency):
        """Format amount with currency symbol"""
        symbol = CURRENCY_SYMBOLS.get(currency, '$')
        if amount >= 1_000_000_000:
            return f"{symbol}{amount/1_000_000_000:.2f}B"
        elif amount >= 1_000_000:
            return f"{symbol}{amount/1_000_000:.2f}M"
        elif amount >= 1_000:
            return f"{symbol}{amount/1_000:.1f}K"
        else:
            return f"{symbol}{amount:,.0f}"
    
    def create_visualizations(self, currency):
        """Create matplotlib visualizations"""
        if not self.results:
            return None
        
        projections = self.results['projections']
        years = [p['Year'] for p in projections]
        net_worth = [p['Net Worth'] for p in projections]
        fire_target = [p['FIRE Target'] for p in projections]
        
        # Create figure with subplots
        fig, axes = plt.subplots(2, 2, figsize=(15, 12))
        fig.suptitle('FIRE Journey Projections', fontsize=16, fontweight='bold')
        
        # Plot 1: Net Worth Growth
        ax1 = axes[0, 0]
        ax1.plot(years, net_worth, 'b-', linewidth=2.5, label='Projected Net Worth')
        ax1.axhline(y=self.results['fire_number'], color='r', linestyle='--', linewidth=2, label='FIRE Target')
        ax1.fill_between(years, net_worth, self.results['fire_number'], 
                        where=[nw >= self.results['fire_number'] for nw in net_worth], 
                        color='green', alpha=0.3, label='FIRE Achieved')
        ax1.fill_between(years, net_worth, self.results['fire_number'], 
                        where=[nw < self.results['fire_number'] for nw in net_worth], 
                        color='orange', alpha=0.3, label='Working Towards FIRE')
        ax1.set_xlabel('Years from Now')
        ax1.set_ylabel(f'Net Worth ({currency})')
        ax1.set_title('Net Worth Growth Projection', fontweight='bold')
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        
        # Plot 2: Scenario Comparison
        ax2 = axes[0, 1]
        scenarios = ['Optimistic', 'Baseline', 'Pessimistic']
        final_values = [
            self.results['optimistic_projection'][-1],
            self.results['last_year_net_worth'],
            self.results['pessimistic_projection'][-1]
        ]
        colors = ['#4CAF50', '#2196F3', '#FF9800']
        bars = ax2.bar(scenarios, final_values, color=colors, edgecolor='black', linewidth=1.5)
        ax2.axhline(y=self.results['fire_number'], color='r', linestyle='--', linewidth=2, label='FIRE Target')
        ax2.set_xlabel('Scenario')
        ax2.set_ylabel(f'Final Net Worth ({currency})')
        ax2.set_title('Final Net Worth by Scenario', fontweight='bold')
        ax2.legend()
        ax2.grid(True, alpha=0.3, axis='y')
        
        # Add value labels on bars
        for bar, value in zip(bars, final_values):
            height = bar.get_height()
            ax2.text(bar.get_x() + bar.get_width()/2., height + max(final_values)*0.01,
                    self.format_currency(value, currency), ha='center', va='bottom', fontweight='bold')
        
        # Plot 3: Progress Gauge
        ax3 = axes[1, 0]
        progress = min(100, (self.results['projections'][0]['Net Worth'] / self.results['fire_number']) * 100)
        theta = np.linspace(0, np.pi, 100)
        r = 1
        x = r * np.cos(theta)
        y = r * np.sin(theta)
        
        ax3.plot(x, y, 'k', linewidth=3)
        
        # Progress arc
        progress_theta = np.linspace(0, (progress/100) * np.pi, 100)
        x_progress = r * np.cos(progress_theta)
        y_progress = r * np.sin(progress_theta)
        ax3.plot(x_progress, y_progress, color='#4CAF50', linewidth=8)
        
        ax3.text(0, 0.2, f'{progress:.1f}%', ha='center', va='center', fontsize=24, fontweight='bold')
        ax3.text(0, -0.2, 'Progress to FIRE', ha='center', va='center', fontsize=12)
        ax3.set_xlim(-1.2, 1.2)
        ax3.set_ylim(-0.2, 1.2)
        ax3.set_aspect('equal')
        ax3.axis('off')
        ax3.set_title('FIRE Progress Gauge', fontweight='bold')
        
        # Plot 4: Yearly Contributions vs Returns
        ax4 = axes[1, 1]
        years_data = years[:min(10, len(years))]  # First 10 years or less
        contributions = []
        returns = []
        
        for i in range(min(10, len(projections))):
            contributions.append(projections[i]['Annual Savings'])
            returns.append(projections[i]['Investment Return'])
        
        x = np.arange(len(years_data))
        width = 0.35
        
        ax4.bar(x - width/2, contributions, width, label='Annual Savings', color='#2196F3', edgecolor='black')
        ax4.bar(x + width/2, returns, width, label='Investment Returns', color='#4CAF50', edgecolor='black')
        
        ax4.set_xlabel('Year')
        ax4.set_ylabel(f'Amount ({currency})')
        ax4.set_title('Savings vs Investment Returns (First 10 Years)', fontweight='bold')
        ax4.set_xticks(x)
        ax4.set_xticklabels([f'Y{int(y)}' for y in years_data])
        ax4.legend()
        ax4.grid(True, alpha=0.3, axis='y')
        
        plt.tight_layout()
        return fig

def main():
    st.markdown('<h1 class="main-header">🔥 FIRE Journey Planner</h1>', unsafe_allow_html=True)
    st.markdown('### Financial Independence, Retire Early Calculator')
    st.markdown('Plan your path to financial freedom with realistic projections and scenarios.')
    
    # Initialize session state
    if 'planner' not in st.session_state:
        st.session_state.planner = FIREPlanner()
    if 'calculations_done' not in st.session_state:
        st.session_state.calculations_done = False
    if 'currency' not in st.session_state:
        st.session_state.currency = 'USD'
    
    # Sidebar
    with st.sidebar:
        st.markdown("## 📘 About FIRE")
        with st.expander("What is FIRE?"):
            st.write("""
            **FIRE (Financial Independence, Retire Early)** is a lifestyle movement focused on:
            
            1. **High Savings Rate**: Typically 50-70% of income
            2. **Investing Wisely**: Low-cost index funds, real estate
            3. **Living Below Means**: Mindful spending
            4. **The 4% Rule**: Withdraw 4% annually from investments in retirement
            
            The goal is to accumulate 25x your annual expenses (based on 4% withdrawal rate).
            """)
        
        with st.expander("Key Principles"):
            st.write("""
            - **The 4% Rule**: Based on the Trinity Study, withdrawing 4% annually from a balanced portfolio historically lasts 30+ years
            - **Compound Interest**: Your money grows exponentially over time
            - **Inflation**: Prices increase 2-3% yearly - your investments must outpace this
            - **Safe Withdrawal Rate**: The percentage you can withdraw annually without depleting your portfolio
            """)
        
        st.markdown("---")
        
        # Currency selector
        st.markdown("## 💱 Currency")
        currency = st.selectbox(
            "Select Currency",
            options=list(CURRENCY_RATES.keys()),
            index=list(CURRENCY_RATES.keys()).index(st.session_state.currency)
        )
        
        # Update currency rate multiplier
        currency_multiplier = CURRENCY_RATES[currency] / CURRENCY_RATES[st.session_state.currency]
        st.session_state.currency = currency
        
        st.markdown(f"**Symbol:** {CURRENCY_SYMBOLS[currency]}")
        st.markdown("*(Note: Rates are approximate for display only)*")
        
        st.markdown("---")
        
        # Donation button
        st.markdown("## ☕ Support This Project")
        st.markdown('[![ko-fi](https://ko-fi.com/img/githubbutton_sm.svg)](https://ko-fi.com/yourusername)')
        st.caption("If you find this tool helpful, consider supporting development.")
        
        st.markdown("---")
        
        # Reset button
        if st.button("🔄 Reset All Inputs"):
            st.session_state.calculations_done = False
            st.rerun()
        
        st.markdown("---")
        
        # Assumptions
        with st.expander("📋 Assumptions & Sources"):
            st.write("""
            **Key Assumptions:**
            - Returns are compounded annually
            - Inflation affects expenses annually
            - Savings occur at year-end
            - No taxes considered (varies by country)
            
            **Historical Benchmarks:**
            - Stock Market: ~7% annual return after inflation
            - Inflation: ~2-3% annually (developed countries)
            - Bond Returns: ~2-3% annual return
            
            **Sources:**
            - Trinity Study (4% Rule)
            - Historical market data (S&P 500)
            - Global inflation statistics
            
            **Disclaimer:** This is educational. Consult a financial advisor.
            """)
    
    # Main content area - Input Section
    st.markdown("## 📊 Your Financial Profile")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        current_age = st.number_input("Current Age", min_value=18, max_value=80, value=30, step=1)
        retirement_age = st.number_input("Desired Retirement Age", min_value=current_age+1, max_value=100, value=45, step=1)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        annual_expenses = st.number_input(
            f"Current Annual Expenses ({CURRENCY_SYMBOLS[currency]})",
            min_value=1000.0,
            max_value=1000000.0,
            value=40000.0,
            step=1000.0,
            help="Your current yearly living expenses"
        )
        current_net_worth = st.number_input(
            f"Current Net Worth ({CURRENCY_SYMBOLS[currency]})",
            min_value=0.0,
            max_value=10000000.0,
            value=50000.0,
            step=10000.0,
            help="Total investments and savings (excluding primary home)"
        )
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col3:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        monthly_savings = st.number_input(
            f"Monthly Savings ({CURRENCY_SYMBOLS[currency]})",
            min_value=0.0,
            max_value=50000.0,
            value=2000.0,
            step=500.0,
            help="Amount you save/invest each month"
        )
        st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown("## ⚙️ Financial Assumptions")
    
    col4, col5, col6 = st.columns(3)
    
    with col4:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        annual_return = st.slider(
            "Expected Annual Investment Return (%)",
            min_value=0.0,
            max_value=20.0,
            value=7.0,
            step=0.1,
            help="Historical average: 7% after inflation for stocks"
        )
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col5:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        inflation = st.slider(
            "Expected Annual Inflation (%)",
            min_value=0.0,
            max_value=10.0,
            value=3.0,
            step=0.1,
            help="Historical average: 2-3% in developed countries"
        )
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col6:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        withdrawal_rate = st.slider(
            "Safe Withdrawal Rate (%)",
            min_value=1.0,
            max_value=10.0,
            value=4.0,
            step=0.1,
            help="4% is the standard (Trinity Study)"
        )
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Calculate button
    if st.button("🚀 Calculate My FIRE Journey", type="primary"):
        with st.spinner("Calculating your path to financial freedom..."):
            params = {
                'current_age': current_age,
                'retirement_age': retirement_age,
                'annual_expenses': annual_expenses,
                'current_net_worth': current_net_worth,
                'monthly_savings': monthly_savings,
                'annual_return': annual_return,
                'inflation': inflation,
                'withdrawal_rate': withdrawal_rate
            }
            
            success = st.session_state.planner.calculate_fire(params)
            st.session_state.calculations_done = success
            
            if success:
                st.success("✅ Calculations complete! See your results below.")
    
    # Display Results
    if st.session_state.calculations_done and st.session_state.planner.results:
        results = st.session_state.planner.results
        planner = st.session_state.planner
        
        st.markdown("---")
        st.markdown("## 📈 Your FIRE Journey Results")
        
        # Success message
        years_to_fire = results['years_to_retirement']
        fire_number_formatted = planner.format_currency(results['fire_number'], currency)
        final_net_worth_formatted = planner.format_currency(results['last_year_net_worth'], currency)
        
        if results['last_year_net_worth'] >= results['fire_number']:
            st.markdown(f"""
            <div class="success-box">
                <h2>🎉 Congratulations!</h2>
                <h3>You'll reach FIRE in <strong>{years_to_fire} years</strong> at age {current_age + years_to_fire}</h3>
                <p>Your target: <strong>{fire_number_formatted}</strong></p>
                <p>Projected net worth at retirement: <strong>{final_net_worth_formatted}</strong></p>
                <p>You're on track to achieve financial independence! 🚀</p>
            </div>
            """, unsafe_allow_html=True)
        else:
            years_needed = years_to_fire
            additional_years = 0
            temp_net_worth = results['last_year_net_worth']
            temp_savings = results['current_annual_savings']
            temp_return = annual_return / 100
            
            # Estimate additional years needed
            while temp_net_worth < results['fire_number'] and additional_years < 40:
                temp_net_worth += temp_savings + (temp_net_worth * temp_return)
                additional_years += 1
            
            st.markdown(f"""
            <div class="info-box">
                <h2>📊 Your Current Path</h2>
                <h3>You'll reach FIRE in <strong>{years_to_fire + additional_years} years</strong> at age {current_age + years_to_fire + additional_years}</h3>
                <p>At your current retirement age ({retirement_age}), you'll need <strong>{planner.format_currency(results['required_monthly_savings'] - monthly_savings, currency)} more monthly</strong> to reach FIRE on time.</p>
                <p>Consider increasing savings or adjusting your timeline.</p>
            </div>
            """, unsafe_allow_html=True)
        
        # Key Metrics
        st.markdown("### 🎯 Key Metrics")
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
            st.metric(
                "FIRE Number",
                planner.format_currency(results['fire_number'], currency),
                "Target net worth"
            )
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col2:
            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
            st.metric(
                "Years to FIRE",
                f"{years_to_fire} years",
                f"Age {current_age + years_to_fire}"
            )
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col3:
            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
            required_savings_diff = results['required_monthly_savings'] - monthly_savings
            diff_text = f"+{planner.format_currency(required_savings_diff, currency)}" if required_savings_diff > 0 else f"{planner.format_currency(required_savings_diff, currency)}"
            st.metric(
                "Monthly Savings Needed",
                planner.format_currency(results['required_monthly_savings'], currency),
                diff_text
            )
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col4:
            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
            progress_pct = min(100, (current_net_worth / results['fire_number']) * 100)
            st.metric(
                "Progress to FIRE",
                f"{progress_pct:.1f}%",
                f"{planner.format_currency(current_net_worth, currency)} / {planner.format_currency(results['fire_number'], currency)}"
            )
            st.progress(progress_pct / 100)
            st.markdown('</div>', unsafe_allow_html=True)
        
        # Visualizations
        st.markdown("### 📊 Visualizations")
        fig = planner.create_visualizations(currency)
        if fig:
            st.pyplot(fig)
        
        # Year-by-Year Projections
        st.markdown("### 📅 Year-by-Year Projections")
        projections_df = pd.DataFrame(results['projections'])
        
        # Format the dataframe for display
        display_df = projections_df.copy()
        display_df['Net Worth'] = display_df['Net Worth'].apply(lambda x: planner.format_currency(x, currency))
        display_df['Annual Savings'] = display_df['Annual Savings'].apply(lambda x: planner.format_currency(x, currency))
        display_df['Investment Return'] = display_df['Investment Return'].apply(lambda x: planner.format_currency(x, currency))
        display_df['Annual Expenses'] = display_df['Annual Expenses'].apply(lambda x: planner.format_currency(x, currency))
        display_df['FIRE Target'] = display_df['FIRE Target'].apply(lambda x: planner.format_currency(x, currency))
        
        # Rename columns for display
        display_df.columns = ['Year', 'Age', 'Net Worth', 'Annual Savings', 'Investment Returns', 
                            'Annual Expenses', 'FIRE Target']
        
        st.dataframe(
            display_df,
            use_container_width=True,
            height=400
        )
        
        # Actionable Insights
        st.markdown("### 💡 Actionable Insights")
        
        col1, col2 = st.columns(2)
        
        with col1:
            with st.expander("🚀 How to Accelerate Your FIRE Journey"):
                st.write("""
                1. **Increase Savings Rate**: Even 5% more can shave years off
                2. **Reduce Expenses**: Track spending, eliminate waste
                3. **Increase Income**: Side hustles, career advancement
                4. **Optimize Investments**: Lower fees, proper asset allocation
                5. **Tax Optimization**: Use tax-advantaged accounts
                """)
        
        with col2:
            with st.expander("📚 Educational Resources"):
                st.write("""
                - **The 4% Rule**: Based on Trinity Study (1998)
                - **Compound Interest**: Albert Einstein's "8th wonder"
                - **Inflation Impact**: Why 3% inflation halves purchasing power in 24 years
                - **Diversification**: Don't put all eggs in one basket
                """)
        
        # Scenario Analysis
        st.markdown("### 🔄 Scenario Analysis")
        
        scenarios = pd.DataFrame({
            'Scenario': ['Optimistic (+25% returns)', 'Baseline', 'Pessimistic (-25% returns)'],
            'Final Net Worth': [
                planner.format_currency(results['optimistic_projection'][-1], currency),
                planner.format_currency(results['last_year_net_worth'], currency),
                planner.format_currency(results['pessimistic_projection'][-1], currency)
            ],
            'Years Difference from Baseline': [
                f"-{max(0, int(years_to_fire * 0.25))} years",
                "0 years",
                f"+{int(years_to_fire * 0.25)} years"
            ]
        })
        
        st.table(scenarios)
        
        # Export functionality
        st.markdown("### 💾 Export Your Plan")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Create CSV for download
            csv = projections_df.to_csv(index=False)
            st.download_button(
                label="📥 Download Projections (CSV)",
                data=csv,
                file_name=f"fire_journey_plan_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv"
            )
        
        with col2:
            # Generate summary report
            summary = f"""
            FIRE JOURNEY PLAN - Generated {datetime.now().strftime('%Y-%m-%d')}
            
            Personal Information:
            - Current Age: {current_age}
            - Target Retirement Age: {retirement_age}
            - Years to FIRE: {years_to_fire}
            
            Financial Summary:
            - Current Annual Expenses: {planner.format_currency(annual_expenses, currency)}
            - Current Net Worth: {planner.format_currency(current_net_worth, currency)}
            - FIRE Target: {planner.format_currency(results['fire_number'], currency)}
            - Current Monthly Savings: {planner.format_currency(monthly_savings, currency)}
            - Required Monthly Savings: {planner.format_currency(results['required_monthly_savings'], currency)}
            
            Assumptions:
            - Expected Annual Return: {annual_return}%
            - Expected Inflation: {inflation}%
            - Safe Withdrawal Rate: {withdrawal_rate}%
            
            Projection:
            - Final Net Worth: {planner.format_currency(results['last_year_net_worth'], currency)}
            - Progress: {(current_net_worth/results['fire_number']*100):.1f}% of way to FIRE
            """
            
            st.download_button(
                label="📄 Download Summary Report",
                data=summary,
                file_name=f"fire_summary_{datetime.now().strftime('%Y%m%d')}.txt",
                mime="text/plain"
            )
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: #666; font-size: 0.9rem;">
        <p>⚠️ <strong>Disclaimer:</strong> This tool provides educational estimates only. 
        Past performance doesn't guarantee future results. 
        Consult with a qualified financial advisor for personal advice.</p>
        <p>Made with ❤️ for the global FIRE community</p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
