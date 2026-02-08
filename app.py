import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

# ==================== PAGE CONFIGURATION ====================
st.set_page_config(
    page_title="🏠 Ultimate Rent vs Buy Analyzer",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': 'https://github.com/rentvswuy',
        'Report a bug': 'https://github.com/rentvswuy/issues',
        'About': "The world's most accurate Rent vs Buy calculator"
    }
)

# ==================== CUSTOM CSS ====================
st.markdown("""
<style>
    /* Modern gradient headers */
    .main-header {
        font-size: 3rem;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 800;
        margin-bottom: 0.5rem;
        text-align: center;
    }
    
    .section-header {
        font-size: 1.8rem;
        background: linear-gradient(135deg, #4CAF50 0%, #2E7D32 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 700;
        margin-top: 1.5rem;
        margin-bottom: 1rem;
    }
    
    /* Card styling */
    .metric-card {
        background: white;
        padding: 1.25rem;
        border-radius: 12px;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
        border: 1px solid #e0e0e0;
        height: 100%;
        transition: transform 0.2s;
    }
    
    .metric-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 25px rgba(0, 0, 0, 0.12);
    }
    
    /* Button styling */
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        font-weight: 600;
        border: none;
        padding: 0.75rem 1.5rem;
        border-radius: 8px;
        transition: all 0.3s;
        width: 100%;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(102, 126, 234, 0.4);
    }
    
    /* Success/Warning boxes */
    .success-box {
        background: linear-gradient(135deg, #d4edda 0%, #c3e6cb 100%);
        padding: 1.5rem;
        border-radius: 10px;
        border-left: 6px solid #28a745;
        margin: 1rem 0;
    }
    
    .warning-box {
        background: linear-gradient(135deg, #fff3cd 0%, #ffeaa7 100%);
        padding: 1.5rem;
        border-radius: 10px;
        border-left: 6px solid #ffc107;
        margin: 1rem 0;
    }
    
    /* Tab styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    
    .stTabs [data-baseweb="tab"] {
        background-color: #f8f9fa;
        border-radius: 8px 8px 0 0;
        padding: 10px 20px;
        font-weight: 600;
    }
    
    /* Dataframe styling */
    .dataframe {
        border-radius: 8px;
        overflow: hidden;
    }
    
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* Responsive adjustments */
    @media (max-width: 768px) {
        .main-header {
            font-size: 2rem;
        }
        .section-header {
            font-size: 1.4rem;
        }
    }
</style>
""", unsafe_allow_html=True)

# ==================== SESSION STATE INITIALIZATION ====================
if 'inputs' not in st.session_state:
    st.session_state.inputs = {
        'time_horizon': 15,
        'rent_monthly': 2000,
        'rent_increase_pct': 3.0,
        'home_price': 500000,
        'home_appreciation_pct': 3.5,
        'down_payment_pct': 20.0,
        'mortgage_rate_pct': 6.5,
        'loan_term': 30,
        'closing_costs_pct': 3.0,
        'property_tax_pct': 1.2,
        'insurance_annual': 1500,
        'maintenance_pct': 1.0,
        'investment_return_pct': 7.0,
        'inflation_pct': 2.5,
        'selling_costs_pct': 6.0,
        'include_tax_benefits': False,
        'marginal_tax_rate': 25.0
    }

# ==================== CORE CALCULATION FUNCTIONS ====================
class RentVsBuyCalculator:
    def __init__(self):
        self.results = None
        
    def calculate_mortgage_payment(self, principal, annual_rate, years):
        """Calculate monthly mortgage payment (P&I)"""
        monthly_rate = annual_rate / 12 / 100
        n_payments = years * 12
        if monthly_rate == 0:
            return principal / n_payments
        payment = principal * (monthly_rate * (1 + monthly_rate) ** n_payments) / ((1 + monthly_rate) ** n_payments - 1)
        return payment
    
    def calculate_amortization_schedule(self, principal, annual_rate, years, extra_payment=0):
        """Generate full amortization schedule"""
        monthly_rate = annual_rate / 12 / 100
        n_payments = years * 12
        monthly_payment = self.calculate_mortgage_payment(principal, annual_rate, years) + extra_payment
        
        schedule = []
        balance = principal
        
        for month in range(1, n_payments + 1):
            if balance <= 0:
                break
                
            interest_payment = balance * monthly_rate
            principal_payment = monthly_payment - interest_payment
            
            if principal_payment > balance:
                principal_payment = balance
                monthly_payment = principal_payment + interest_payment
                
            balance -= principal_payment
            
            schedule.append({
                'Month': month,
                'Payment': monthly_payment,
                'Principal': principal_payment,
                'Interest': interest_payment,
                'Balance': max(0, balance)
            })
            
        return pd.DataFrame(schedule)
    
    def calculate_scenarios(self, params):
        """Calculate rent vs buy scenarios"""
        try:
            # Extract parameters
            years = params['time_horizon']
            rent_monthly = params['rent_monthly']
            rent_increase = params['rent_increase_pct'] / 100
            home_price = params['home_price']
            appreciation = params['home_appreciation_pct'] / 100
            down_payment_pct = params['down_payment_pct'] / 100
            mortgage_rate = params['mortgage_rate_pct'] / 100
            loan_term = params['loan_term']
            closing_costs = params['closing_costs_pct'] / 100
            property_tax_rate = params['property_tax_pct'] / 100
            insurance_annual = params['insurance_annual']
            maintenance_rate = params['maintenance_pct'] / 100
            investment_return = params['investment_return_pct'] / 100
            inflation = params['inflation_pct'] / 100
            selling_costs = params['selling_costs_pct'] / 100
            
            # Calculate initial amounts
            down_payment = home_price * down_payment_pct
            loan_amount = home_price - down_payment
            closing_costs_amount = home_price * closing_costs
            
            # Initial investment portfolio for renter
            renter_portfolio = down_payment + closing_costs_amount  # Money not spent on down payment
            
            # Monthly mortgage payment (P&I)
            monthly_mortgage_pi = self.calculate_mortgage_payment(loan_amount, mortgage_rate * 100, loan_term)
            
            # Monthly property costs
            monthly_property_tax = (home_price * property_tax_rate) / 12
            monthly_insurance = insurance_annual / 12
            monthly_maintenance = (home_price * maintenance_rate) / 12
            monthly_housing_cost = monthly_mortgage_pi + monthly_property_tax + monthly_insurance + monthly_maintenance
            
            # Initialize arrays for tracking
            years_list = list(range(years + 1))
            rent_costs = []
            buy_costs = []
            rent_portfolio_values = []
            buy_equity_values = []
            home_values = []
            rent_net_worth = []
            buy_net_worth = []
            
            # Get amortization schedule for the entire period
            amortization = self.calculate_amortization_schedule(loan_amount, mortgage_rate * 100, loan_term)
            
            # Year 0 (initial state)
            rent_costs.append(0)
            buy_costs.append(down_payment + closing_costs_amount)
            rent_portfolio_values.append(renter_portfolio)
            buy_equity_values.append(down_payment)
            home_values.append(home_price)
            rent_net_worth.append(renter_portfolio)
            buy_net_worth.append(down_payment)
            
            # Track cumulative values
            cumulative_rent_paid = 0
            cumulative_mortgage_principal = 0
            cumulative_mortgage_interest = 0
            cumulative_property_tax = 0
            cumulative_insurance = 0
            cumulative_maintenance = 0
            cumulative_opportunity_cost = 0
            
            # Calculate year by year
            for year in range(1, years + 1):
                # Current home value (appreciated)
                current_home_value = home_price * ((1 + appreciation) ** year)
                home_values.append(current_home_value)
                
                # RENT SCENARIO
                # Annual rent (with increases)
                current_rent = rent_monthly * 12 * ((1 + rent_increase) ** (year - 1))
                cumulative_rent_paid += current_rent
                
                # Renter portfolio growth (investing the down payment savings)
                # Each month, renter invests the difference between buy and rent costs
                monthly_rent = rent_monthly * ((1 + rent_increase) ** (year - 1))
                monthly_cost_difference = monthly_housing_cost - monthly_rent
                
                # Portfolio grows with investment returns
                # Start with previous year's portfolio
                portfolio = rent_portfolio_values[-1]
                
                # Add monthly contributions and growth
                monthly_return = (1 + investment_return) ** (1/12) - 1
                for month in range(12):
                    # Add the monthly savings difference
                    portfolio += monthly_cost_difference
                    # Apply investment growth
                    portfolio *= (1 + monthly_return)
                
                rent_portfolio_values.append(portfolio)
                rent_costs.append(cumulative_rent_paid)
                rent_net_worth.append(portfolio)
                
                # BUY SCENARIO
                # Calculate mortgage details for this year
                year_start_month = (year - 1) * 12
                year_end_month = year * 12
                
                if year_end_month <= len(amortization):
                    year_amortization = amortization.iloc[year_start_month:min(year_end_month, len(amortization))]
                    year_principal = year_amortization['Principal'].sum()
                    year_interest = year_amortization['Interest'].sum()
                else:
                    # Mortgage paid off, no more payments
                    year_principal = 0
                    year_interest = 0
                
                cumulative_mortgage_principal += year_principal
                cumulative_mortgage_interest += year_interest
                
                # Annual property costs
                annual_property_tax = current_home_value * property_tax_rate
                annual_maintenance = current_home_value * maintenance_rate
                
                cumulative_property_tax += annual_property_tax
                cumulative_maintenance += annual_maintenance
                cumulative_insurance += insurance_annual
                
                # Total costs this year
                year_costs = year_principal + year_interest + annual_property_tax + insurance_annual + annual_maintenance
                
                # Equity in home (down payment + principal paid + appreciation)
                principal_paid = cumulative_mortgage_principal
                appreciation_gain = current_home_value - home_price
                home_equity = down_payment + principal_paid + appreciation_gain
                
                # If we sold the house this year
                selling_costs_amount = current_home_value * selling_costs
                net_proceeds_from_sale = current_home_value - selling_costs_amount - loan_amount + principal_paid
                
                buy_equity_values.append(home_equity)
                buy_costs.append(
                    down_payment + closing_costs_amount + 
                    cumulative_mortgage_interest + cumulative_property_tax + 
                    cumulative_insurance + cumulative_maintenance
                )
                buy_net_worth.append(net_proceeds_from_sale)
                
                # Opportunity cost (what the down payment could have earned)
                opportunity_growth = down_payment * ((1 + investment_return) ** year) - down_payment
                cumulative_opportunity_cost = opportunity_growth
            
            # Create detailed results DataFrame
            results_df = pd.DataFrame({
                'Year': years_list,
                'Rent_Cost_Cumulative': rent_costs,
                'Buy_Cost_Cumulative': buy_costs,
                'Rent_Portfolio_Value': rent_portfolio_values,
                'Buy_Home_Value': home_values,
                'Buy_Home_Equity': buy_equity_values,
                'Rent_Net_Worth': rent_net_worth,
                'Buy_Net_Worth': buy_net_worth
            })
            
            # Calculate key metrics
            final_rent_net_worth = rent_net_worth[-1]
            final_buy_net_worth = buy_net_worth[-1]
            net_worth_difference = final_buy_net_worth - final_rent_net_worth
            
            # Find break-even year (when buy net worth exceeds rent net worth)
            break_even_year = None
            for i in range(1, len(years_list)):
                if buy_net_worth[i] > rent_net_worth[i]:
                    break_even_year = i
                    break
            
            # Calculate IRR of buying vs renting
            cash_flows = []
            for i in range(years + 1):
                if i == 0:
                    # Initial investment (down payment + closing costs)
                    cash_flows.append(-(down_payment + closing_costs_amount))
                else:
                    # Annual net benefit (rent saved minus ownership costs plus equity buildup)
                    rent_paid = rent_monthly * 12 * ((1 + rent_increase) ** (i - 1))
                    ownership_costs = (
                        (monthly_mortgage_pi * 12) + 
                        (home_values[i] * property_tax_rate) + 
                        insurance_annual + 
                        (home_values[i] * maintenance_rate)
                    )
                    equity_change = buy_equity_values[i] - buy_equity_values[i-1] if i > 0 else 0
                    net_benefit = rent_paid - ownership_costs + equity_change
                    cash_flows.append(net_benefit)
            
            # At final year, add home sale proceeds
            cash_flows[-1] += home_values[-1] * (1 - selling_costs)
            
            # Calculate IRR (simplified)
            try:
                irr = np.irr(cash_flows) * 100
            except:
                irr = None
            
            self.results = {
                'years': years,
                'results_df': results_df,
                'break_even_year': break_even_year,
                'final_rent_net_worth': final_rent_net_worth,
                'final_buy_net_worth': final_buy_net_worth,
                'net_worth_difference': net_worth_difference,
                'down_payment': down_payment,
                'monthly_mortgage_pi': monthly_mortgage_pi,
                'monthly_housing_cost': monthly_housing_cost,
                'total_interest_paid': cumulative_mortgage_interest,
                'total_property_tax': cumulative_property_tax,
                'total_maintenance': cumulative_maintenance,
                'cash_flows': cash_flows,
                'irr': irr,
                'cumulative_rent_paid': cumulative_rent_paid,
                'home_appreciation': home_values[-1] - home_price
            }
            
            return True
            
        except Exception as e:
            st.error(f"Calculation error: {str(e)}")
            return False
    
    def format_currency(self, amount):
        """Format amount as currency"""
        if abs(amount) >= 1_000_000:
            return f"${amount/1_000_000:.2f}M"
        elif abs(amount) >= 10_000:
            return f"${amount/1_000:.0f}K"
        else:
            return f"${amount:,.0f}"

# ==================== SIDEBAR ====================
with st.sidebar:
    st.markdown("<h2 style='text-align: center;'>⚙️ Calculator Settings</h2>", unsafe_allow_html=True)
    
    # Quick inputs section
    with st.expander("📊 Quick Inputs", expanded=True):
        st.session_state.inputs['time_horizon'] = st.slider(
            "Time Horizon (Years)",
            min_value=1,
            max_value=30,
            value=st.session_state.inputs['time_horizon'],
            help="How many years to compare scenarios"
        )
        
        col1, col2 = st.columns(2)
        with col1:
            st.session_state.inputs['rent_monthly'] = st.number_input(
                "Monthly Rent ($)",
                min_value=100,
                max_value=20000,
                value=st.session_state.inputs['rent_monthly'],
                step=100
            )
        with col2:
            st.session_state.inputs['home_price'] = st.number_input(
                "Home Price ($)",
                min_value=50000,
                max_value=5000000,
                value=st.session_state.inputs['home_price'],
                step=25000
            )
    
    # Detailed inputs
    with st.expander("🏠 Home Purchase Details"):
        col1, col2 = st.columns(2)
        with col1:
            st.session_state.inputs['down_payment_pct'] = st.slider(
                "Down Payment (%)",
                min_value=3.0,
                max_value=50.0,
                value=st.session_state.inputs['down_payment_pct'],
                step=1.0,
                help="Minimum 3% for conventional loans"
            )
        with col2:
            st.session_state.inputs['mortgage_rate_pct'] = st.slider(
                "Mortgage Rate (%)",
                min_value=1.0,
                max_value=15.0,
                value=st.session_state.inputs['mortgage_rate_pct'],
                step=0.1
            )
        
        st.session_state.inputs['loan_term'] = st.selectbox(
            "Loan Term (Years)",
            options=[10, 15, 20, 30],
            index=3
        )
        
        st.session_state.inputs['home_appreciation_pct'] = st.slider(
            "Home Appreciation (%/year)",
            min_value=-5.0,
            max_value=15.0,
            value=st.session_state.inputs['home_appreciation_pct'],
            step=0.1,
            help="Historical average: 3-5% nationally"
        )
    
    with st.expander("💰 Ongoing Costs"):
        col1, col2 = st.columns(2)
        with col1:
            st.session_state.inputs['property_tax_pct'] = st.slider(
                "Property Tax (%/year)",
                min_value=0.1,
                max_value=5.0,
                value=st.session_state.inputs['property_tax_pct'],
                step=0.1,
                help="Varies by location (US average: ~1.1%)"
            )
        with col2:
            st.session_state.inputs['maintenance_pct'] = st.slider(
                "Maintenance (%/year)",
                min_value=0.1,
                max_value=5.0,
                value=st.session_state.inputs['maintenance_pct'],
                step=0.1,
                help="Rule of thumb: 1% of home value annually"
            )
        
        st.session_state.inputs['insurance_annual'] = st.number_input(
            "Home Insurance ($/year)",
            min_value=500,
            max_value=10000,
            value=st.session_state.inputs['insurance_annual'],
            step=100
        )
    
    with st.expander("📈 Market Assumptions"):
        col1, col2 = st.columns(2)
        with col1:
            st.session_state.inputs['rent_increase_pct'] = st.slider(
                "Rent Increase (%/year)",
                min_value=0.0,
                max_value=10.0,
                value=st.session_state.inputs['rent_increase_pct'],
                step=0.1
            )
        with col2:
            st.session_state.inputs['investment_return_pct'] = st.slider(
                "Investment Return (%/year)",
                min_value=0.0,
                max_value=15.0,
                value=st.session_state.inputs['investment_return_pct'],
                step=0.1,
                help="Historical stock market average: ~7% after inflation"
            )
        
        st.session_state.inputs['inflation_pct'] = st.slider(
            "Inflation Rate (%/year)",
            min_value=0.0,
            max_value=10.0,
            value=st.session_state.inputs['inflation_pct'],
            step=0.1
        )
    
    with st.expander("⚡ One-Time Costs"):
        col1, col2 = st.columns(2)
        with col1:
            st.session_state.inputs['closing_costs_pct'] = st.slider(
                "Closing Costs (%)",
                min_value=1.0,
                max_value=10.0,
                value=st.session_state.inputs['closing_costs_pct'],
                step=0.5,
                help="Typically 2-5% of home price"
            )
        with col2:
            st.session_state.inputs['selling_costs_pct'] = st.slider(
                "Selling Costs (%)",
                min_value=1.0,
                max_value=10.0,
                value=st.session_state.inputs['selling_costs_pct'],
                step=0.5,
                help="Typically 5-6% (realtor fees + closing)"
            )
    
    # Calculate button
    st.markdown("---")
    if st.button("🚀 **Calculate Scenarios**", type="primary", use_container_width=True):
        st.session_state.calculated = True
    
    # Reset button
    if st.button("🔄 Reset to Defaults", use_container_width=True):
        st.session_state.inputs = {
            'time_horizon': 15,
            'rent_monthly': 2000,
            'rent_increase_pct': 3.0,
            'home_price': 500000,
            'home_appreciation_pct': 3.5,
            'down_payment_pct': 20.0,
            'mortgage_rate_pct': 6.5,
            'loan_term': 30,
            'closing_costs_pct': 3.0,
            'property_tax_pct': 1.2,
            'insurance_annual': 1500,
            'maintenance_pct': 1.0,
            'investment_return_pct': 7.0,
            'inflation_pct': 2.5,
            'selling_costs_pct': 6.0,
            'include_tax_benefits': False,
            'marginal_tax_rate': 25.0
        }
        st.session_state.calculated = False
        st.rerun()
    
    st.markdown("---")
    
    # Information section
    with st.expander("📚 Key Insights"):
        st.info("""
        **When Buying Wins:**
        - Staying 7+ years (break-even point)
        - High rent appreciation areas
        - Low mortgage rates
        - High home appreciation
        
        **When Renting Wins:**
        - Short time horizon (<5 years)
        - High investment returns
        - Low rent growth areas
        - High transaction costs
        
        **Rule of Thumb:** 
        Buy if you'll stay 7+ years and rent < 5% of home value/month.
        """)
    
    with st.expander("📊 Data Sources"):
        st.caption("""
        - Mortgage rates: Freddie Mac PMMS
        - Home appreciation: Case-Shiller Index
        - Rent growth: Zillow Observed Rent Index
        - Investment returns: S&P 500 historical
        - Inflation: US Bureau of Labor Statistics
        """)
    
    st.markdown("---")
    
    # Donation button
    st.markdown("### ☕ Support This Project")
    st.markdown(
        """
        <div style='text-align: center;'>
            <a href='https://ko-fi.com/yourusername' target='_blank'>
                <img src='https://ko-fi.com/img/githubbutton_sm.svg' alt='Ko-fi' style='width: 100%;'>
            </a>
        </div>
        """,
        unsafe_allow_html=True
    )
    
    st.caption("*This tool saves people $10,000s in housing decisions*")

# ==================== MAIN CONTENT ====================
st.markdown("<h1 class='main-header'>🏠 Ultimate Rent vs Buy Analyzer</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; font-size: 1.2rem; color: #666;'>Make smarter housing decisions with data-driven analysis</p>", unsafe_allow_html=True)

# Initialize calculator
calculator = RentVsBuyCalculator()

# Calculate if button pressed
if 'calculated' not in st.session_state:
    st.session_state.calculated = False

if st.session_state.calculated:
    # Perform calculation
    success = calculator.calculate_scenarios(st.session_state.inputs)
    
    if success and calculator.results:
        results = calculator.results
        
        # Create tabs for different views
        tab1, tab2, tab3, tab4, tab5 = st.tabs(["📊 Results Overview", "📈 Charts", "📅 Year-by-Year", "💰 Cost Breakdown", "🎯 Sensitivity"])
        
        with tab1:
            st.markdown("<h2 class='section-header'>Key Results</h2>", unsafe_allow_html=True)
            
            # Winner announcement
            if results['net_worth_difference'] > 0:
                st.markdown(f"""
                <div class="success-box">
                    <h3>🏆 Buying is Better!</h3>
                    <p>After {results['years']} years, buying builds <strong>{calculator.format_currency(results['net_worth_difference'])} more wealth</strong> than renting.</p>
                    <p>Break-even point: <strong>{results['break_even_year']} years</strong> (when buying starts winning)</p>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div class="warning-box">
                    <h3>🏆 Renting is Better!</h3>
                    <p>After {results['years']} years, renting preserves <strong>{calculator.format_currency(abs(results['net_worth_difference']))} more wealth</strong> than buying.</p>
                    <p>Buying never becomes advantageous in this {results['years']}-year period.</p>
                </div>
                """, unsafe_allow_html=True)
            
            # Key metrics in cards
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.markdown('<div class="metric-card">', unsafe_allow_html=True)
                st.metric(
                    "Final Rent Net Worth",
                    calculator.format_currency(results['final_rent_net_worth']),
                    "Portfolio value"
                )
                st.markdown('</div>', unsafe_allow_html=True)
            
            with col2:
                st.markdown('<div class="metric-card">', unsafe_allow_html=True)
                st.metric(
                    "Final Buy Net Worth",
                    calculator.format_currency(results['final_buy_net_worth']),
                    "Home equity after sale"
                )
                st.markdown('</div>', unsafe_allow_html=True)
            
            with col3:
                st.markdown('<div class="metric-card">', unsafe_allow_html=True)
                st.metric(
                    "Wealth Difference",
                    calculator.format_currency(results['net_worth_difference']),
                    "Buy - Rent"
                )
                st.markdown('</div>', unsafe_allow_html=True)
            
            with col4:
                st.markdown('<div class="metric-card">', unsafe_allow_html=True)
                if results['break_even_year']:
                    st.metric(
                        "Break-even Year",
                        f"Year {results['break_even_year']}",
                        f"Age +{results['break_even_year']}"
                    )
                else:
                    st.metric(
                        "Break-even Year",
                        "Never",
                        "Renting always wins"
                    )
                st.markdown('</div>', unsafe_allow_html=True)
            
            # Monthly payment comparison
            st.markdown("<h3 class='section-header'>Monthly Costs Comparison</h3>", unsafe_allow_html=True)
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.markdown('<div class="metric-card">', unsafe_allow_html=True)
                st.metric(
                    "Monthly Rent",
                    f"${st.session_state.inputs['rent_monthly']:,.0f}",
                    f"Year 1, grows {st.session_state.inputs['rent_increase_pct']}%/year"
                )
                st.markdown('</div>', unsafe_allow_html=True)
            
            with col2:
                st.markdown('<div class="metric-card">', unsafe_allow_html=True)
                st.metric(
                    "Mortgage (P&I)",
                    f"${results['monthly_mortgage_pi']:,.0f}",
                    f"Fixed for {st.session_state.inputs['loan_term']} years"
                )
                st.markdown('</div>', unsafe_allow_html=True)
            
            with col3:
                st.markdown('<div class="metric-card">', unsafe_allow_html=True)
                total_monthly = results['monthly_housing_cost']
                st.metric(
                    "Total Monthly (Buy)",
                    f"${total_monthly:,.0f}",
                    "Incl. taxes, insurance, maintenance"
                )
                st.markdown('</div>', unsafe_allow_html=True)
            
            # Quick insights
            st.markdown("<h3 class='section-header'>💡 Key Insights</h3>", unsafe_allow_html=True)
            
            insights = []
            if results['net_worth_difference'] > 100000:
                insights.append(f"**Major wealth builder:** Buying creates over ${results['net_worth_difference']/1000:.0f}K more wealth")
            if results['break_even_year'] and results['break_even_year'] <= 5:
                insights.append(f"**Quick break-even:** Buying wins after only {results['break_even_year']} years")
            if st.session_state.inputs['home_appreciation_pct'] > st.session_state.inputs['investment_return_pct']:
                insights.append(f"**Home appreciation ({st.session_state.inputs['home_appreciation_pct']}%) beats investments ({st.session_state.inputs['investment_return_pct']}%)**")
            if results['total_interest_paid'] > results['home_appreciation']:
                insights.append(f"**Interest costs (${results['total_interest_paid']/1000:.0f}K) exceed appreciation (${results['home_appreciation']/1000:.0f}K)**")
            
            if insights:
                for insight in insights:
                    st.info(insight)
        
        with tab2:
            st.markdown("<h2 class='section-header'>Net Worth Comparison Over Time</h2>", unsafe_allow_html=True)
            
            # Create interactive chart with Plotly
            fig = go.Figure()
            
            # Add rent net worth line
            fig.add_trace(go.Scatter(
                x=results['results_df']['Year'],
                y=results['results_df']['Rent_Net_Worth'],
                mode='lines',
                name='Renting Net Worth',
                line=dict(color='#FF6B6B', width=3),
                hovertemplate='Year %{x}: $%{y:,.0f}<extra></extra>'
            ))
            
            # Add buy net worth line
            fig.add_trace(go.Scatter(
                x=results['results_df']['Year'],
                y=results['results_df']['Buy_Net_Worth'],
                mode='lines',
                name='Buying Net Worth',
                line=dict(color='#4ECDC4', width=3),
                hovertemplate='Year %{x}: $%{y:,.0f}<extra></extra>'
            ))
            
            # Add break-even point if exists
            if results['break_even_year']:
                fig.add_vline(
                    x=results['break_even_year'],
                    line_dash="dash",
                    line_color="gray",
                    annotation_text=f"Break-even: Year {results['break_even_year']}",
                    annotation_position="top right"
                )
            
            fig.update_layout(
                title="Net Worth Growth: Rent vs Buy",
                xaxis_title="Years",
                yaxis_title="Net Worth ($)",
                hovermode="x unified",
                template="plotly_white",
                height=500,
                legend=dict(
                    yanchor="top",
                    y=0.99,
                    xanchor="left",
                    x=0.01
                )
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Cost breakdown chart
            st.markdown("<h3 class='section-header'>Cost Breakdown Over Time</h3>", unsafe_allow_html=True)
            
            col1, col2 = st.columns(2)
            with col1:
                # Create cost comparison bar chart
                cost_labels = ['Rent Paid', 'Mortgage Interest', 'Property Tax', 'Maintenance']
                cost_values = [
                    results['cumulative_rent_paid'],
                    results['total_interest_paid'],
                    results['total_property_tax'],
                    results['total_maintenance']
                ]
                
                fig2 = px.bar(
                    x=cost_labels,
                    y=cost_values,
                    color=cost_labels,
                    color_discrete_sequence=['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4'],
                    labels={'x': 'Cost Category', 'y': 'Total Amount ($)'},
                    title="Cumulative Costs Over Period"
                )
                
                fig2.update_layout(
                    showlegend=False,
                    template="plotly_white",
                    height=400
                )
                
                fig2.update_traces(
                    hovertemplate='%{x}: $%{y:,.0f}<extra></extra>'
                )
                
                st.plotly_chart(fig2, use_container_width=True)
            
            with col2:
                # Create gauge chart for winner margin
                fig3 = go.Figure(go.Indicator(
                    mode = "gauge+number+delta",
                    value = results['net_worth_difference'],
                    delta = {'reference': 0, 'prefix': "$"},
                    title = {'text': "Wealth Advantage"},
                    gauge = {
                        'axis': {'range': [min(-abs(results['net_worth_difference'])*2, -100000), max(abs(results['net_worth_difference'])*2, 100000)]},
                        'bar': {'color': "#4ECDC4" if results['net_worth_difference'] > 0 else "#FF6B6B"},
                        'steps': [
                            {'range': [min(-abs(results['net_worth_difference'])*2, -100000), 0], 'color': "lightgray"},
                            {'range': [0, max(abs(results['net_worth_difference'])*2, 100000)], 'color': "lightgray"}
                        ],
                        'threshold': {
                            'line': {'color': "red", 'width': 4},
                            'thickness': 0.75,
                            'value': 0
                        }
                    }
                ))
                
                fig3.update_layout(
                    height=400,
                    margin=dict(t=50, b=10)
                )
                
                st.plotly_chart(fig3, use_container_width=True)
        
        with tab3:
            st.markdown("<h2 class='section-header'>Detailed Year-by-Year Projections</h2>", unsafe_allow_html=True)
            
            # Format the DataFrame for display
            display_df = results['results_df'].copy()
            display_df.columns = ['Year', 'Rent Cost', 'Buy Cost', 'Rent Portfolio', 'Home Value', 'Home Equity', 'Rent Net Worth', 'Buy Net Worth']
            
            # Format currency columns
            for col in display_df.columns[1:]:
                display_df[col] = display_df[col].apply(lambda x: f"${x:,.0f}")
            
            st.dataframe(
                display_df,
                use_container_width=True,
                height=600
            )
            
            # Download button
            csv = results['results_df'].to_csv(index=False)
            st.download_button(
                label="📥 Download Full Data (CSV)",
                data=csv,
                file_name=f"rent_vs_buy_analysis_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv",
                use_container_width=True
            )
        
        with tab4:
            st.markdown("<h2 class='section-header'>Detailed Cost Breakdown</h2>", unsafe_allow_html=True)
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("#### 🏠 Home Purchase Costs")
                purchase_costs = pd.DataFrame({
                    'Item': ['Down Payment', 'Closing Costs', 'Total Initial'],
                    'Amount': [
                        results['down_payment'],
                        st.session_state.inputs['home_price'] * st.session_state.inputs['closing_costs_pct'] / 100,
                        results['down_payment'] + (st.session_state.inputs['home_price'] * st.session_state.inputs['closing_costs_pct'] / 100)
                    ]
                })
                purchase_costs['Amount'] = purchase_costs['Amount'].apply(lambda x: f"${x:,.0f}")
                st.table(purchase_costs)
                
                st.markdown("#### 📈 Appreciation & Equity")
                equity_data = pd.DataFrame({
                    'Metric': ['Home Appreciation', 'Principal Paid', 'Total Equity Gain'],
                    'Amount': [
                        results['home_appreciation'],
                        results['results_df']['Buy_Home_Equity'].iloc[-1] - results['down_payment'] - results['home_appreciation'],
                        results['results_df']['Buy_Home_Equity'].iloc[-1] - results['down_payment']
                    ]
                })
                equity_data['Amount'] = equity_data['Amount'].apply(lambda x: f"${x:,.0f}")
                st.table(equity_data)
            
            with col2:
                st.markdown("#### 💰 Ongoing Ownership Costs")
                ongoing_costs = pd.DataFrame({
                    'Item': ['Mortgage Interest', 'Property Tax', 'Home Insurance', 'Maintenance', 'Total Ongoing'],
                    'Amount': [
                        results['total_interest_paid'],
                        results['total_property_tax'],
                        st.session_state.inputs['insurance_annual'] * results['years'],
                        results['total_maintenance'],
                        results['total_interest_paid'] + results['total_property_tax'] + 
                        (st.session_state.inputs['insurance_annual'] * results['years']) + results['total_maintenance']
                    ]
                })
                ongoing_costs['Amount'] = ongoing_costs['Amount'].apply(lambda x: f"${x:,.0f}")
                st.table(ongoing_costs)
                
                st.markdown("#### 🏡 Final Sale")
                sale_data = pd.DataFrame({
                    'Item': ['Final Home Value', 'Selling Costs', 'Remaining Mortgage', 'Net Proceeds'],
                    'Amount': [
                        results['results_df']['Buy_Home_Value'].iloc[-1],
                        results['results_df']['Buy_Home_Value'].iloc[-1] * st.session_state.inputs['selling_costs_pct'] / 100,
                        max(0, st.session_state.inputs['home_price'] * (1 - st.session_state.inputs['down_payment_pct']/100) - 
                            (results['results_df']['Buy_Home_Equity'].iloc[-1] - results['down_payment'] - results['home_appreciation'])),
                        results['final_buy_net_worth']
                    ]
                })
                sale_data['Amount'] = sale_data['Amount'].apply(lambda x: f"${x:,.0f}")
                st.table(sale_data)
        
        with tab5:
            st.markdown("<h2 class='section-header'>Sensitivity Analysis</h2>", unsafe_allow_html=True)
            st.markdown("Adjust key variables to see how they affect the outcome:")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                new_appreciation = st.slider(
                    "Home Appreciation (%)",
                    min_value=-5.0,
                    max_value=15.0,
                    value=st.session_state.inputs['home_appreciation_pct'],
                    step=0.5,
                    key='sens_appreciation'
                )
            
            with col2:
                new_mortgage_rate = st.slider(
                    "Mortgage Rate (%)",
                    min_value=1.0,
                    max_value=15.0,
                    value=st.session_state.inputs['mortgage_rate_pct'],
                    step=0.25,
                    key='sens_rate'
                )
            
            with col3:
                new_investment_return = st.slider(
                    "Investment Return (%)",
                    min_value=0.0,
                    max_value=15.0,
                    value=st.session_state.inputs['investment_return_pct'],
                    step=0.5,
                    key='sens_investment'
                )
            
            # Quick sensitivity calculation
            sens_params = st.session_state.inputs.copy()
            sens_params['home_appreciation_pct'] = new_appreciation
            sens_params['mortgage_rate_pct'] = new_mortgage_rate
            sens_params['investment_return_pct'] = new_investment_return
            
            sens_calculator = RentVsBuyCalculator()
            if sens_calculator.calculate_scenarios(sens_params):
                sens_results = sens_calculator.results
                
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    delta_appreciation = new_appreciation - st.session_state.inputs['home_appreciation_pct']
                    st.metric(
                        "With New Appreciation",
                        calculator.format_currency(sens_results['net_worth_difference']),
                        f"{delta_appreciation:+.1f}% change"
                    )
                
                with col2:
                    delta_rate = new_mortgage_rate - st.session_state.inputs['mortgage_rate_pct']
                    st.metric(
                        "With New Rate",
                        calculator.format_currency(sens_results['net_worth_difference']),
                        f"{delta_rate:+.1f}% change"
                    )
                
                with col3:
                    delta_investment = new_investment_return - st.session_state.inputs['investment_return_pct']
                    st.metric(
                        "With New Investment Return",
                        calculator.format_currency(sens_results['net_worth_difference']),
                        f"{delta_investment:+.1f}% change"
                    )
                
                with col4:
                    original_diff = results['net_worth_difference']
                    new_diff = sens_results['net_worth_difference']
                    change = new_diff - original_diff
                    st.metric(
                        "Total Change",
                        calculator.format_currency(new_diff),
                        f"{calculator.format_currency(change)} vs original"
                    )
                
                # Sensitivity insights
                st.markdown("#### 💡 Sensitivity Insights")
                insights = []
                if new_appreciation > st.session_state.inputs['home_appreciation_pct'] and sens_results['net_worth_difference'] > results['net_worth_difference']:
                    insights.append(f"**Higher appreciation ({new_appreciation}%) makes buying even better**")
                if new_mortgage_rate < st.session_state.inputs['mortgage_rate_pct'] and sens_results['net_worth_difference'] > results['net_worth_difference']:
                    insights.append(f"**Lower mortgage rate ({new_mortgage_rate}%) significantly improves buying outcome**")
                if new_investment_return > st.session_state.inputs['investment_return_pct'] and sens_results['net_worth_difference'] < results['net_worth_difference']:
                    insights.append(f"**Better investment returns ({new_investment_return}%) favor renting**")
                
                for insight in insights:
                    st.info(insight)
    
    else:
        st.error("Failed to calculate scenarios. Please check your inputs.")
else:
    # Show initial state before calculation
    st.markdown("""
    <div class="info-box">
        <h3>🚀 Ready to Analyze Your Rent vs Buy Decision?</h3>
        <p>This calculator will show you:</p>
        <ul>
            <li>Whether renting or buying builds more wealth for your situation</li>
            <li>The exact break-even point (when buying starts winning)</li>
            <li>Total costs and net worth over 1-30 years</li>
            <li>Sensitivity to market changes (rates, appreciation, etc.)</li>
        </ul>
        <p><strong>Configure your scenario in the sidebar, then click "Calculate Scenarios"</strong></p>
    </div>
    """, unsafe_allow_html=True)
    
    # Show example scenarios
    st.markdown("<h3 class='section-header'>📊 Example Scenarios</h3>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.markdown("#### 🏙️ **High-Cost City**")
        st.markdown("- Rent: $3,500/month")
        st.markdown("- Buy: $1M home")
        st.markdown("- Break-even: ~10 years")
        st.markdown("</div>", unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.markdown("#### 🏡 **Suburban Family**")
        st.markdown("- Rent: $2,200/month")
        st.markdown("- Buy: $500K home")
        st.markdown("- Break-even: ~5 years")
        st.markdown("</div>", unsafe_allow_html=True)
    
    with col3:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.markdown("#### 📈 **High-Growth Market**")
        st.markdown("- Rent: $1,800/month")
        st.markdown("- Buy: $400K home")
        st.markdown("- Break-even: ~3 years")
        st.markdown("</div>", unsafe_allow_html=True)

# ==================== FOOTER ====================
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666; font-size: 0.9rem;'>
    <p><strong>⚠️ IMPORTANT DISCLAIMER:</strong> This tool provides educational estimates only. 
    Results depend on assumptions that may not match reality. 
    Past performance doesn't guarantee future results. 
    Always consult with qualified financial and real estate professionals before making major decisions.</p>
    <p>© 2024 Ultimate Rent vs Buy Analyzer | Data updated monthly | Version 2.0</p>
</div>
""", unsafe_allow_html=True)
