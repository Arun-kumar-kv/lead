# app/services/vacancy_dashboard_service.py
"""
Vacancy Dashboard service implementing HYBRID approach:
- Uses snapshot tables for historical/trend data (fast)
- Uses live queries for current activity (accurate)
"""

from sqlalchemy.orm import Session
from datetime import datetime, date, timedelta
from typing import Dict, Any, List
from app.repositories.vacancy_repo import VacancyRepository
import logging

logger = logging.getLogger(__name__)


class VacancyDashboardService:
    """
    Main service for Vacancy Dashboard
    Combines live data with historical snapshots
    """
    
    def __init__(self, db: Session):
        self.db = db
        self.vacancy_repo = VacancyRepository(db)
    
    def get_dashboard_data(self) -> Dict[str, Any]:
        """
        Get complete vacancy dashboard data using HYBRID approach
        
        HYBRID STRATEGY:
        1. Current metrics → Live queries (real-time)
        2. Historical context → Snapshot tables (fast)
        3. Trends → Snapshot tables (fast)
        4. Comparisons → Combine both
        
        Matches the UI requirements from the uploaded screenshot
        """
        
        # # Get latest snapshot for historical context
        # latest_snapshot = self.vacancy_repo.get_latest_snapshot()
        
        # # Get previous month's snapshot for comparison
        # prev_month_snapshot = None
        # if latest_snapshot:
        #     prev_month_date = latest_snapshot.DATE - timedelta(days=30)
        #     prev_snapshots = self.vacancy_repo.get_snapshot_date_range(
        #         prev_month_date - timedelta(days=5),
        #         prev_month_date + timedelta(days=5)
        #     )
        #     prev_month_snapshot = prev_snapshots[0] if prev_snapshots else None
        
        # ====================================================================
        # LIVE QUERIES (Current State)
        # ====================================================================
        
        # Top metrics cards
        vacant_units_now = self.vacancy_repo.get_vacant_units_live()
        total_units = self.vacancy_repo.get_total_units_live()
        occupied_units = self.vacancy_repo.get_occupied_units_live()
        vacancy_rate = self.vacancy_repo.get_vacancy_rate_live()
        avg_vacancy_days = self.vacancy_repo.get_avg_vacancy_days_live()
        rent_ready_unleased = self.vacancy_repo.get_rent_ready_unleased_live()
        maintenance_downtime = self.vacancy_repo.get_maintenance_downtime_units_live()
        # re_leased_30d = self.vacancy_repo.get_re_leased_in_period_live(30)
        # re_leased_90d = self.vacancy_repo.get_re_leased_in_period_live(90)
        
        # Current breakdowns
        vacancy_by_property_live = self.vacancy_repo.get_vacancy_by_property_live()
        vacancy_by_unit_type_live = self.vacancy_repo.get_vacancy_by_unit_type_live()
        duration_buckets_live = self.vacancy_repo.get_vacancy_duration_buckets_live()
        # BASIC METRICS
        rent_ready_unleased = self.vacancy_repo.get_rent_ready_unleased_live()
        maintenance_downtime = self.vacancy_repo.get_maintenance_downtime_units_live()
        # re_leased_30d = self.vacancy_repo.get_re_leased_in_period_live(30)

        # OPTIONAL: If you don't have weekly comparison yet
        new_rent_ready_this_week = 0
        re_leased_change = 0

        # Vacancy Trend Data (make sure this exists)
        # vacancy_trend = self.vacancy_repo.get_vacancy_trend_live()  # or whatever your method is
              
        # ====================================================================
        # SNAPSHOT QUERIES (Historical Trends - Fast)
        # ====================================================================
        
        # vacancy_trend = self.vacancy_repo.get_vacancy_trend_from_snapshot(days=365)
        # move_in_out_trend = self.vacancy_repo.get_move_in_out_trend_from_snapshot(months=12)
        
        # ====================================================================
        # CALCULATE COMPARISONS
        # ====================================================================
        
        # Compare with last month
        vacant_units_change = 0
        avg_days_change = 0
        rent_ready_change = 0
        re_leased_change = 0
        
        # if latest_snapshot and prev_month_snapshot:
        #     vacant_units_change = vacant_units_now - prev_month_snapshot.VACANT_UNITS
        #     avg_days_change = avg_vacancy_days - float(prev_month_snapshot.AVG_VACANCY_DAYS)
        #     rent_ready_change = rent_ready_unleased - prev_month_snapshot.RENT_READY_UNLEASED
        #     re_leased_change = re_leased_30d - prev_month_snapshot.RE_LEASED_30D
        
        # # Calculate "this week" change for rent-ready
        # week_ago_date = datetime.utcnow().date() - timedelta(days=7)
        # week_ago_snapshot = self.vacancy_repo.get_snapshot_date_range(
        #     week_ago_date - timedelta(days=2),
        #     week_ago_date + timedelta(days=2)
        # )
        # new_rent_ready_this_week = 0
        # if week_ago_snapshot:
        #     new_rent_ready_this_week = rent_ready_unleased - week_ago_snapshot[0].RENT_READY_UNLEASED
        
        # ====================================================================
        # BUILD RESPONSE (Matching UI Structure)
        # ====================================================================
        
        return {
            # Top KPI Cards
            'kpi_cards': {
                'vacant_units': {
                    'value': vacant_units_now,
                    'change': vacant_units_change,
                    'change_period': 'vs last month',
                    'trend': 'up' if vacant_units_change > 0 else 'down'
                },
                'avg_vacancy_days': {
                    'value': avg_vacancy_days,
                    'change': avg_days_change,
                    'change_period': 'days vs prev',
                    'trend': 'up' if avg_days_change > 0 else 'down'
                },
                'rent_ready_unleased': {
                    'value': rent_ready_unleased,
                    'change': new_rent_ready_this_week,
                    'change_period': 'new this week',
                    'trend': 'up' if new_rent_ready_this_week > 0 else 'stable'
                },
                # 're_leased_30d': {
                #     'value': re_leased_30d,
                #     'change': re_leased_change,
                #     'change_period': 'vs last month',
                #     'trend': 'down' if re_leased_change < 0 else 'up',
                #     'benchmark': 94  # From UI
                # },
                'maintenance_downtime': {
                    'value': maintenance_downtime,
                    'label': 'units blocked'
                }
            },
            
            # Vacancy Rate Trend Chart
            # 'vacancy_rate_trend': {
            #     'title': 'Vacancy Rate Trend',
            #     'subtitle': 'Monthly occupancy vs vacancy - click bar to drill',
            #     'data': self._format_vacancy_trend_for_chart(vacancy_trend),
            #     'current_vacancy_rate': vacancy_rate,
            #     'is_rising': self._is_trend_rising(vacancy_trend)
            # },
            
            # Vacancy by Property Chart
            'vacancy_by_property': {
                'title': 'Vacancy by Property',
                'subtitle': 'Top 10 properties by vacant unit count',
                'data': vacancy_by_property_live[:15],  # Top 5
                'drill_available': True
            },
            
            # Vacancy Duration Buckets (Donut Chart)
            'vacancy_duration_buckets': {
                'title': 'Vacancy Duration Buckets',
                'subtitle': 'Units by days vacant - 30/60/90/90+',
                'data': [
                    {'label': '0-30 days', 'value': duration_buckets_live.get('0-30 days', 0), 'color': '#10b981'},
                    {'label': '31-60 days', 'value': duration_buckets_live.get('31-60 days', 0), 'color': '#f59e0b'},
                    {'label': '61-90 days', 'value': duration_buckets_live.get('61-90 days', 0), 'color': '#f97316'},
                    {'label': '90+ days', 'value': duration_buckets_live.get('90+ days', 0), 'color': '#ef4444'}
                ],
                'aging_risk': duration_buckets_live.get('90+ days', 0)
            },
            
            # Vacancy by Unit Type Chart
            'vacancy_by_unit_type': {
                'title': 'Vacancy by Unit Type',
                'subtitle': '1BHK / 2BHK / 3BHK / Studio / Commercial',
                'data': self._format_unit_type_for_chart(vacancy_by_unit_type_live),
                'config_view': True
            },
            
            # Move-In vs Move-Out Seasonality
            # 'move_in_out_seasonality': {
            #     'title': 'Move-In vs Move-Out Seasonality',
            #     'subtitle': '12-month pattern - identify peak churn months',
            #     'data': self._format_move_in_out_for_chart(move_in_out_trend),
            #     'seasonal_insight': self._get_seasonal_insight(move_in_out_trend)
            # },
            
            # Summary Metrics
            'summary': {
                'total_units': total_units,
                'vacant_units': vacant_units_now,
                'occupied_units': occupied_units,
                'vacancy_rate': vacancy_rate,
                'avg_vacancy_days': avg_vacancy_days,
                # 'snapshot_date': str(latest_snapshot.DATE) if latest_snapshot else None
            },
            
            # # Financial Impact
            # 'financial_impact': {
            #     'monthly_loss': float(latest_snapshot.MONTHLY_LOSS) if latest_snapshot else 0.0,
            #     'annual_projection': float(latest_snapshot.MONTHLY_LOSS) * 12 if latest_snapshot else 0.0
            # },
            
            # Metadata
            'last_updated': datetime.utcnow().isoformat(),
            'data_sources': {
                'live_queries': [
                    'vacant_units', 'avg_vacancy_days', 'rent_ready_unleased',
                    'maintenance_downtime', 'vacancy_by_property', 'vacancy_by_unit_type',
                    'duration_buckets'
                ],
                'snapshot_queries': [
                    'vacancy_trend', 'move_in_out_trend', 'financial_impact'
                ]
            }
        }
    
    # ========================================================================
    # HELPER METHODS FOR DATA FORMATTING
    # ========================================================================
    
    def _format_vacancy_trend_for_chart(self, trend_data: List[Dict]) -> List[Dict]:
        """
        Format vacancy trend for stacked bar chart
        Groups by month to reduce data points
        """
        # Group by month
        monthly_data = {}
        for item in trend_data:
            month_key = f"{item['year']}-{item['month']}"
            if month_key not in monthly_data:
                monthly_data[month_key] = {
                    'month': item['month'],
                    'year': item['year'],
                    'occupied': 0,
                    'vacant': 0
                }
            # Use latest data for that month
            monthly_data[month_key]['occupied'] = item['occupied_units']
            monthly_data[month_key]['vacant'] = item['vacant_units']
        
        # Convert to list and sort
        result = list(monthly_data.values())
        result.sort(key=lambda x: (x['year'], x['month']))
        
        # Return last 12 months
        return result[-12:]
    
    # def _format_unit_type_for_chart(self, unit_type_data: List[Dict]) -> List[Dict]:
    #     """Format unit type data for grouped bar chart"""
    #     return [
    #         {
    #             'unit_type': item['unit_type'],
    #             'vacant': item['vacant_units'],
    #             'occupied': item['occupied_units'],
    #             'vacancy_rate': item['vacancy_rate']
    #         }
    #         for item in unit_type_data
    #     ]
    def _format_unit_type_for_chart(self, unit_type_data: List[Dict]) -> List[Dict]:
        return [
            {
                'unit_type': item['unit_type'],
                'vacant': item['vacant_units'],
                'occupied': item['occupied_units'],
                'vacancy_rate': item.get('vacancy_percentage', 0)  # ✅ FIX
            }
            for item in unit_type_data
        ]    
    def _format_move_in_out_for_chart(self, trend_data: List[Dict]) -> List[Dict]:
        """Format move-in/out data for line chart"""
        return [
            {
                'month': item['month_name'],
                'year': item['year'],
                'move_ins': item['move_ins'],
                'move_outs': item['move_outs'],
                'net_change': item['net_change']
            }
            for item in trend_data
        ]
    
    def _is_trend_rising(self, trend_data: List[Dict]) -> bool:
        """Determine if vacancy trend is rising"""
        if len(trend_data) < 2:
            return False
        
        recent = trend_data[-3:]  # Last 3 data points
        if len(recent) < 2:
            return False
        
        # Check if vacancy rate is increasing
        rates = [item['vacancy_rate'] for item in recent]
        return rates[-1] > rates[0]
    
    def _get_seasonal_insight(self, trend_data: List[Dict]) -> str:
        """Generate insight about move-in/out seasonality"""
        if not trend_data:
            return "Insufficient data"
        
        # Find peak move-out month
        max_move_outs = max(trend_data, key=lambda x: x['move_outs'])
        max_move_ins = max(trend_data, key=lambda x: x['move_ins'])
        
        return f"Peak move-outs: {max_move_outs['month_name']}, Peak move-ins: {max_move_ins['month_name']}"
    
    # ========================================================================
    # ADDITIONAL ANALYSIS METHODS
    # ========================================================================
    
    def get_property_drill_down(self, property_id: int) -> Dict[str, Any]:
        """Get detailed vacancy data for a specific property"""
        # This would be called when user clicks on a property
        # Returns detailed breakdown for that property
        pass
    
    def get_aging_units_alert(self, days_threshold: int = 90) -> List[Dict]:
        """Get units vacant for more than threshold days (for alerts)"""
        # Returns list of units at risk
        pass
    
    def get_financial_analysis(self) -> Dict[str, Any]:
        """Get detailed financial impact analysis"""
        # Returns revenue loss breakdown by property, unit type, etc.
        pass