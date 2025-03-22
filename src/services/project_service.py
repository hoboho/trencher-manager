def get_all(self, page=1, per_page=20):
        """Get all projects with pagination"""
        try:
            offset = (page - 1) * per_page
            total = self.session.query(Project).count()
            projects = self.session.query(Project).order_by(Project.created_at.desc()).offset(offset).limit(per_page).all()
            return projects, total
        except Exception as e:
            self.logger.error(f"Error getting projects: {str(e)}")
            return [], 0 