from flask import current_app


def paginate(query, page=1, per_page=None):
    """
    Paginate a SQLAlchemy query
    
    Args:
        query: SQLAlchemy query object
        page: Page number (1-indexed)
        per_page: Items per page (defaults to config value)
    
    Returns:
        dict with 'items' and 'pagination' keys
    """
    if per_page is None:
        per_page = current_app.config.get('ITEMS_PER_PAGE', 20)
    
    # Enforce max per_page
    max_per_page = current_app.config.get('MAX_ITEMS_PER_PAGE', 100)
    per_page = min(per_page, max_per_page)
    
    # Ensure valid page number
    page = max(1, page)
    
    # Execute pagination
    paginated = query.paginate(
        page=page,
        per_page=per_page,
        error_out=False
    )
    
    return {
        'items': paginated.items,
        'pagination': {
            'page': paginated.page,
            'per_page': paginated.per_page,
            'total_items': paginated.total,
            'total_pages': paginated.pages,
            'has_next': paginated.has_next,
            'has_prev': paginated.has_prev,
            'next_page': paginated.next_num if paginated.has_next else None,
            'prev_page': paginated.prev_num if paginated.has_prev else None
        }
    }