from flask import Blueprint, request, jsonify, render_template
from app import db
from datetime import datetime, timedelta
import json

enterprise_bp = Blueprint('enterprise_bp', __name__, url_prefix='/enterprise')

@enterprise_bp.route('/')
def dashboard():
    return render_template('enterprise_dashboard/index.html')

@enterprise_bp.route('/enterprises')
def enterprises():
    return render_template('enterprise_dashboard/enterprises.html')

@enterprise_bp.route('/meetings')
def meetings():
    return render_template('enterprise_dashboard/meetings.html')

@enterprise_bp.route('/reports')
def reports():
    return render_template('enterprise_dashboard/reports.html')

# API Routes
@enterprise_bp.route('/api/enterprises', methods=['GET'])
def get_enterprises():
    from src.models.enterprise_models import get_models
    Enterprise, EnterpriseMeeting = get_models(db)
    try:
        page = request.args.get('page', 1, type=int)
        limit = request.args.get('limit', 20, type=int)
        search = request.args.get('search', '')
        priority = request.args.get('priority', '')
        ai_platform = request.args.get('ai_platform', '')
        industry = request.args.get('industry', '')

        # Build query
        query = db.session.query(Enterprise)

        if search:
            query = query.filter(
                db.or_(
                    Enterprise.enterprise_name.contains(search),
                    Enterprise.base_location.contains(search)
                )
            )

        if priority:
            query = query.filter(Enterprise.priority == priority)

        if ai_platform:
            query = query.filter(Enterprise.ai_platform == ai_platform)

        if industry:
            query = query.filter(Enterprise.industry.contains(industry))

        # Get total count
        total = query.count()

        # Apply pagination
        start_idx = (page - 1) * limit
        enterprises = query.offset(start_idx).limit(limit).all()

        return jsonify({
            'enterprises': [e.to_dict() for e in enterprises],
            'total': total,
            'page': page,
            'pages': (total + limit - 1) // limit  # Calculate pages
        })
    except Exception as e:
        import traceback
        print(f"Error in get_enterprises: {e}")
        print(traceback.format_exc())
        return jsonify({'error': str(e)}), 500

@enterprise_bp.route('/api/enterprises', methods=['POST'])
def create_enterprise():
    from src.models.enterprise_models import get_models
    Enterprise, EnterpriseMeeting = get_models(db)
    try:
        data = request.get_json()

        # Validate required fields
        required_fields = ['enterprise_name', 'ai_platform', 'lead_inbound_time', 'priority']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400

        # Check if enterprise name already exists
        existing = Enterprise.query.filter_by(enterprise_name=data['enterprise_name']).first()
        if existing:
            return jsonify({'error': 'Enterprise with this name already exists'}), 400

        enterprise = Enterprise(
            enterprise_name=data['enterprise_name'],
            ai_platform=data['ai_platform'],
            lead_inbound_time=data['lead_inbound_time'],
            partner_level=data.get('partner_level'),
            ai_products=data.get('ai_products', ''),
            priority=data['priority'],
            base_location=data.get('base_location', ''),
            registered_capital=data.get('registered_capital'),
            employee_count=data.get('employee_count'),
            enterprise_background=data.get('enterprise_background', ''),
            industry=','.join(data.get('industry', [])) if data.get('industry') else '',
            task_direction=data.get('task_direction', ''),
            contact_info=data.get('contact_info', ''),
            usage_scenario=data.get('usage_scenario', ''),
            progress=[]
        )

        db.session.add(enterprise)
        db.session.commit()

        return jsonify({'success': True, 'enterprise': enterprise.to_dict()})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@enterprise_bp.route('/api/enterprises/<int:id>', methods=['GET'])
def get_enterprise(id):
    from src.models.enterprise_models import get_models
    Enterprise, EnterpriseMeeting = get_models(db)
    try:
        enterprise = Enterprise.query.get_or_404(id)
        return jsonify({'enterprise': enterprise.to_dict()})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@enterprise_bp.route('/api/enterprise/metrics', methods=['GET'])
def api_enterprise_metrics():
    from src.models.enterprise_models import get_models
    Enterprise, EnterpriseMeeting = get_models(db)
    try:
        from datetime import datetime, timedelta
        now = datetime.utcnow()
        one_week_ago = now - timedelta(days=7)

        # Get metrics from the database
        total_enterprises = Enterprise.query.count()
        p0_enterprises = Enterprise.query.filter_by(priority='P0').count()

        # Calculate pending enterprises (those without progress or with no progress)
        pending_enterprises = 0
        enterprises = Enterprise.query.all()
        for enterprise in enterprises:
            if not enterprise.progress or len(enterprise.progress) == 0:
                pending_enterprises += 1

        # Get enterprises with progress in the last week
        weekly_progress = 0  # Count enterprises with updates in the last week
        for enterprise in enterprises:
            if enterprise.lead_update_time and enterprise.lead_update_time >= one_week_ago:
                weekly_progress += 1

        # Get enterprises that have submitted products
        submitted_products = 0
        for enterprise in enterprises:
            if enterprise.ai_products and enterprise.ai_products.strip() != '':
                submitted_products += 1

        # For weekly meetings, we need meeting data
        weekly_meetings = 0
        try:
            meetings = EnterpriseMeeting.query.all()
            for meeting in meetings:
                if meeting.meeting_time and meeting.meeting_time >= one_week_ago:
                    weekly_meetings += 1
        except Exception as e:
            # If EnterpriseMeeting has issues, continue with 0
            print(f"Error counting meetings: {e}")
            pass

        return jsonify({
            'total_enterprises': total_enterprises,
            'p0_enterprises': p0_enterprises,
            'pending_enterprises': pending_enterprises,
            'weekly_progress': weekly_progress,
            'submitted_products': submitted_products,
            'weekly_meetings': weekly_meetings
        })
    except Exception as e:
        import traceback
        print(f"Error in api_enterprise_metrics: {e}")
        print(traceback.format_exc())
        return jsonify({'error': str(e)}), 500

@enterprise_bp.route('/api/enterprise/charts/industry', methods=['GET'])
def api_enterprise_industry_chart():
    from src.models.enterprise_models import get_models
    Enterprise, EnterpriseMeeting = get_models(db)
    try:
        # First, get all enterprises and process industries manually
        enterprises = Enterprise.query.all()

        # Process the results to handle comma-separated industries
        industry_count = {}
        for enterprise in enterprises:
            if enterprise.industry:  # If industry field is not None
                industries = enterprise.industry.split(',')
                for ind in industries:
                    ind = ind.strip()
                    if ind:  # If not empty
                        industry_count[ind] = industry_count.get(ind, 0) + 1

        # Sort by count descending and limit to top 10
        sorted_industries = sorted(industry_count.items(), key=lambda x: x[1], reverse=True)[:10]

        labels = [item[0] for item in sorted_industries]
        values = [item[1] for item in sorted_industries]

        return jsonify({
            'labels': labels,
            'values': values
        })
    except Exception as e:
        import traceback
        print(f"Error in api_enterprise_industry_chart: {e}")
        print(traceback.format_exc())
        return jsonify({'error': str(e)}), 500

@enterprise_bp.route('/api/enterprise/charts/ai-platform', methods=['GET'])
def api_enterprise_ai_platform_chart():
    from src.models.enterprise_models import get_models
    Enterprise, EnterpriseMeeting = get_models(db)
    try:
        # Get AI platform distribution from the database
        enterprises = Enterprise.query.all()

        platform_count = {}
        for enterprise in enterprises:
            if enterprise.ai_platform:
                platform_count[enterprise.ai_platform] = platform_count.get(enterprise.ai_platform, 0) + 1

        labels = list(platform_count.keys())
        values = list(platform_count.values())

        return jsonify({
            'labels': labels,
            'values': values
        })
    except Exception as e:
        import traceback
        print(f"Error in api_enterprise_ai_platform_chart: {e}")
        print(traceback.format_exc())
        return jsonify({'error': str(e)}), 500

@enterprise_bp.route('/api/enterprise/charts/progress', methods=['GET'])
def api_enterprise_progress_chart():
    from src.models.enterprise_models import get_models
    Enterprise, EnterpriseMeeting = get_models(db)
    try:
        # Get priority distribution from the database
        enterprises = Enterprise.query.all()

        priority_count = {}
        for enterprise in enterprises:
            if enterprise.priority:
                priority_count[enterprise.priority] = priority_count.get(enterprise.priority, 0) + 1

        labels = list(priority_count.keys())
        values = list(priority_count.values())

        return jsonify({
            'labels': labels,
            'values': values
        })
    except Exception as e:
        import traceback
        print(f"Error in api_enterprise_progress_chart: {e}")
        print(traceback.format_exc())
        return jsonify({'error': str(e)}), 500

@enterprise_bp.route('/api/enterprise/charts/trend', methods=['GET'])
def api_enterprise_trend_chart():
    from src.models.enterprise_models import get_models
    Enterprise, EnterpriseMeeting = get_models(db)
    try:
        # Get P0 enterprises trend over the past 12 weeks
        from datetime import datetime, timedelta
        from sqlalchemy import func

        # Get the start date (12 weeks ago from today)
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(weeks=12)

        trend_data = []
        current_date = start_date

        # Generate data points for each week
        for i in range(13):  # 13 weeks to get 12 intervals
            week_end = start_date + timedelta(weeks=i)

            if week_end > end_date:
                break

            # Count P0 enterprises created up to this week
            p0_count = Enterprise.query.filter(
                Enterprise.priority == 'P0',
                Enterprise.created_at <= week_end
            ).count()

            # Format week label
            week_label = week_end.strftime('%Y-W%U')
            trend_data.append({
                'week': week_label,
                'count': p0_count
            })

        return jsonify({
            'data': trend_data
        })
    except Exception as e:
        import traceback
        print(f"Error in api_enterprise_trend_chart: {e}")
        print(traceback.format_exc())
        return jsonify({'error': str(e)}), 500

@enterprise_bp.route('/api/meetings', methods=['GET'])
def get_meetings():
    from src.models.enterprise_models import get_models
    Enterprise, EnterpriseMeeting = get_models(db)
    try:
        page = request.args.get('page', 1, type=int)
        limit = request.args.get('limit', 20, type=int)
        search = request.args.get('search', '')

        # Build query
        query = db.session.query(EnterpriseMeeting)

        if search:
            query = query.filter(
                db.or_(
                    EnterpriseMeeting.enterprise_name.contains(search),
                    EnterpriseMeeting.meeting_summary.contains(search)
                )
            )

        # Get total count
        total = query.count()

        # Apply pagination
        start_idx = (page - 1) * limit
        meetings = query.offset(start_idx).limit(limit).all()

        return jsonify({
            'meetings': [m.to_dict() for m in meetings],
            'total': total,
            'page': page,
            'pages': (total + limit - 1) // limit  # Calculate pages
        })
    except Exception as e:
        import traceback
        print(f"Error in get_meetings: {e}")
        print(traceback.format_exc())
        return jsonify({'error': str(e)}), 500