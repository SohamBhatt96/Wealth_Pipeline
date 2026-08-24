def calculate_position_size(account_capital, risk_percentage, entry_price, stop_loss_price):
    """Calculates exact shares to buy based on fixed fractional risk."""
    risk_amount = account_capital * (risk_percentage / 100)
    risk_per_share = entry_price - stop_loss_price
    
    if risk_per_share <= 0:
        return {'Shares to Buy': 0, 'Total Trade Value (₹)': 0}
        
    shares = int(risk_amount / risk_per_share)
    total_value = round(shares * entry_price, 2)
    
    return {
        'Shares to Buy': shares,
        'Total Trade Value (₹)': total_value
    }