@app.route('/api/dashboard/stats', methods=['GET'])
@login_required
def api_dashboard_stats():
    """API endpoint for dashboard statistics."""
    try:
        # Get user's recent reports from database
        recent_reports = Report.query.filter_by(user_id=current_user.id)\
            .order_by(Report.created_at.desc())\
            .limit(10)\
            .all()

        # Calculate statistics
        total_reports = Report.query.filter_by(user_id=current_user.id).count()
        completed_reports = Report.query.filter_by(user_id=current_user.id, status='completed').count()
        processing_reports = Report.query.filter_by(user_id=current_user.id, status='processing').count()

        stats = {
            'total_reports': total_reports,
            'completed_reports': completed_reports,
            'processing_reports': processing_reports,
            'recent_reports': [{
                'id': report.id,
                'report_id': report.report_id,
                'title': report.title,
                'city': report.city,
                'industry': report.industry,
                'status': report.status,
                'created_at': report.created_at.isoformat(),
                'completed_at': report.completed_at.isoformat() if report.completed_at else None
            } for report in recent_reports]
        }

        return jsonify({'success': True, 'data': stats})

    except Exception as e:
        logger.error(f"Dashboard stats error: {e}")
        return jsonify({'success': False, 'message': '获取统计数据失败'}), 500


@app.route('/api/reports', methods=['GET'])
@login_required
def api_reports_list():
    """API endpoint for reports list."""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        
        reports = Report.query.filter_by(user_id=current_user.id)\
            .order_by(Report.created_at.desc())\
            .paginate(page=page, per_page=per_page, error_out=False)

        return jsonify({
            'success': True,
            'data': {
                'reports': [{
                    'id': report.id,
                    'report_id': report.report_id,
                    'title': report.title,
                    'city': report.city,
                    'industry': report.industry,
                    'report_type': report.report_type,
                    'status': report.status,
                    'created_at': report.created_at.isoformat(),
                    'completed_at': report.completed_at.isoformat() if report.completed_at else None
                } for report in reports.items],
                'pagination': {
                    'page': page,
                    'per_page': per_page,
                    'total': reports.total,
                    'pages': reports.pages
                }
            }
        })

    except Exception as e:
        logger.error(f"Reports list error: {e}")
        return jsonify({'success': False, 'message': '获取报告列表失败'}), 500


@app.route('/api/upload', methods=['POST'])
@login_required
def api_upload_file():
    """API endpoint for file upload."""
    try:
        if 'file' not in request.files:
            return jsonify({'success': False, 'message': '没有选择文件'}), 400

        file = request.files['file']
        
        if file.filename == '':
            return jsonify({'success': False, 'message': '没有选择文件'}), 400

        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            unique_filename = f"{timestamp}_{filename}"
            
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
            file.save(file_path)

            # Create report record
            report = Report(
                report_id=f"upload_{timestamp}",
                title=f"上传报告_{unique_filename}",
                report_type='upload',
                file_path=file_path,
                user_id=current_user.id,
                status='pending'
            )
            db.session.add(report)
            db.session.commit()

            # Process file asynchronously
            # For now, we'll just return the successful upload
            # In a real implementation, we would start an async task

            return jsonify({
                'success': True,
                'message': '文件上传成功',
                'report_id': report.report_id,
                'filename': unique_filename
            })

        return jsonify({'success': False, 'message': '不支持的文件格式'}), 400

    except Exception as e:
        logger.error(f"Upload error: {e}")
        return jsonify({'success': False, 'message': '上传失败'}), 500


@app.route('/api/reports/<report_id>', methods=['GET'])
@login_required
def api_get_report(report_id):
    """API endpoint to get a single report."""
    try:
        report = Report.query.filter_by(report_id=report_id, user_id=current_user.id).first()
        
        if not report:
            return jsonify({'success': False, 'message': '报告不存在'}), 404

        # Load report data from file
        report_data = None
        if report.report_type == 'llm':
            expected_path = APP_ROOT / 'data' / 'output' / 'llm_reports' / f"{report_id}.json"
            file_path = expected_path
            # Fallback to stored file_path if default missing
            if not file_path.exists() and report.file_path:
                alt_path = Path(report.file_path)
                if alt_path.exists():
                    file_path = alt_path
        else:
            file_path = Path(report.file_path)

        if file_path.exists():
            with open(file_path, 'r', encoding='utf-8') as f:
                report_data = json.load(f)

        return jsonify({
            'success': True,
            'data': {
                'id': report.id,
                'report_id': report.report_id,
                'title': report.title,
                'city': report.city,
                'industry': report.industry,
                'report_type': report.report_type,
                'status': report.status,
                'created_at': report.created_at.isoformat(),
                'completed_at': report.completed_at.isoformat() if report.completed_at else None,
                'file_path': report.file_path,
                'report_data': report_data
            }
        })

    except Exception as e:
        logger.error(f"Get report error: {e}")
        return jsonify({'success': False, 'message': '获取报告失败'}), 500


# Legacy Routes (for backward compatibility)
@app.route('/')
@login_required
def index():
    """Main dashboard page with API status and notifications (legacy route)."""
    try:
        # Get user's recent reports from database
        recent_reports = Report.query.filter_by(user_id=current_user.id)\
            .order_by(Report.created_at.desc())\
            .limit(10)\
            .all()

        # Get user notifications
        user_notifications = notification_service.get_user_notifications(str(current_user.id))
        notification_stats = notification_service.get_notification_stats(str(current_user.id))

        # Get API error summary
        api_error_summary = api_error_handler.get_error_summary()

        return render_template('index_enhanced.html',
                             recent_reports=recent_reports,
                             user=current_user,
                             notifications=user_notifications,
                             notification_stats=notification_stats,
                             api_error_summary=api_error_summary)
    except Exception as e:
        logger.error(f"Error in index route: {e}")
        # Even if notifications fail, show the main dashboard
        return render_template('index_enhanced.html',
                             recent_reports=[],
                             user=current_user,
                             notifications=[],
                             notification_stats={'total': 0, 'unread': 0, 'has_recent_errors': False},
                            api_error_summary={'status': 'ok', 'message': 'No recent errors'})


@app.route('/logo_preview')
@login_required
def logo_preview():
    return render_template('logo_preview.html')

@app.route('/streaming-generate-report', methods=['GET', 'POST'])
def streaming_generate_report():
    """Streaming report generation page with real-time content display (legacy route)."""
    if request.method == 'POST':
        city = request.form.get('city')
        industry = request.form.get('industry')
        additional_context = request.form.get('additional_context', '')
        llm_service = request.form.get('llm_service', 'kimi')

        if not city or not industry:
            flash('请输入城市和行业名称', 'error')
            return render_template('generate_report.html')

        # Render streaming template with form data
        return render_template('streaming_generate.html',
                             city=city,
                             industry=industry,
                             additional_context=additional_context,
                             llm_service=llm_service)

    # GET request - handle query parameters or show basic form
    city = request.args.get('city', '上海')
    industry = request.args.get('industry', '人工智能')
    additional_context = request.args.get('additional_context', '')
    llm_service = request.args.get('llm_service', 'kimi')

    return render_template('streaming_generate.html',
                         city=city,
                         industry=industry,
                         additional_context=additional_context,
                         llm_service=llm_service)