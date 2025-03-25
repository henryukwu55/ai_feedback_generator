import requests
import os


#https://elu.instructure.com/courses/335/gradebook/speed_grader?assignment_id=4691&student_id=403
#https://elu.instructure.com/courses/109/assignments/3364/submissions/123 // sandbox

class CanvasAPI:
    def __init__(self, domain, token):
        self.domain = domain
        self.token = token
        self.base_url = f'https://{domain}/api/v1'
        self.headers = {
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json'
        }

    def get_all_pages(self, url, params=None):
        """Handles Canvas API pagination"""
        if params is None:
            params = {}
        
        results = []
        while url:
            response = requests.get(url, headers=self.headers, params=params)
            response.raise_for_status()
            results.extend(response.json())
            
            # Get the next page URL from the Link header
            links = requests.utils.parse_header_links(response.headers.get('Link', '').rstrip('>').replace('>,<', ',<'))
            url = None
            for link in links:
                if link['rel'] == 'next':
                    url = link['url']
                    params = {}  # Params are included in the next URL
                    break
                    
        return results

    def get_course_assignments(self, course_id):
        """Get all assignments for a course"""
        url = f'{self.base_url}/courses/{course_id}/assignments'
        return self.get_all_pages(url)

    def get_course_students(self, course_id):
        """Get all students in a course"""
        url = f'{self.base_url}/courses/{course_id}/users'
        params = {'enrollment_type[]': 'student'}
        return self.get_all_pages(url, params)

    def get_assignment_submissions(self, course_id, assignment_id):
        """Get all submissions for an assignment"""
        url = f'{self.base_url}/courses/{course_id}/assignments/{assignment_id}/submissions'
        params = {'include[]': ['submission_comments', 'user']}
        return self.get_all_pages(url, params)


    def download_submission_content(self, submission):
        """Return list of (filename, content) tuples from submission"""
        files = []
        submission_type = submission.get('submission_type')
        
        if submission_type == 'online_upload':
            for attachment in submission.get('attachments', []):
                try:
                    response = requests.get(attachment['url'], headers=self.headers)
                    if response.status_code == 200:
                        files.append((attachment['filename'], response.content))
                except Exception as e:
                    print(f"Error downloading attachment: {e}")
        
        elif submission_type == 'online_text_entry':
            text = submission.get('body', '')
            if text:
                files.append(('submission.txt', text.encode('utf-8')))
        
        elif submission_type == 'online_url':
            url = submission.get('url', '')
            if url:
                files.append(('url.txt', url.encode('utf-8')))
        
        return files
    
    def submit_submission_comment(self, course_id, assignment_id, student_id, comment_text, is_group_comment=False):
        """Submit a text comment on a student's submission"""
        # The correct endpoint includes 'comments' in the path
        url = f'{self.base_url}/courses/{course_id}/assignments/{assignment_id}/submissions/{student_id}/comments/114277'
        url= "https://elu.instructure.com/courses/109/assignments/562/submissions/123/"
        headers = self.headers.copy()
        headers['Content-Type'] = 'application/json'  # Changed to JSON content type
        
        # Data should be JSON formatted
        data = {
            'comment': {
                'text_comment': comment_text,
                'group_comment': is_group_comment
            }
        }
        
        print(f"Submitting comment to URL: {url}")
        print(f"With data: {data}")
        
        # Use json parameter instead of data for JSON payload
        response = requests.put(url, headers=headers, json=data)
        print(f"Response status: {response.status_code}")
        print(f"Response body: {response.text}")
        
        response.raise_for_status()
        return response.json()


    def submit_submission_file_comment(self, course_id, assignment_id, student_id, file_path, is_group_comment=False):
        """Submit a file as a comment on a student's submission"""
        url = f'{self.base_url}/courses/{course_id}/assignments/{assignment_id}/submissions/{student_id}/comments/files'
        
        # First, get a file upload URL
        resp_1 = requests.post(url, headers=self.headers)
        resp_1.raise_for_status()
        upload_url = resp_1.json()['upload_url']
        upload_params = resp_1.json()['upload_params']
        
        # Prepare the file for upload
        with open(file_path, 'rb') as file:
            files = {'file': file}
            # Merge the upload_params with our file
            response = requests.post(upload_url, data=upload_params, files=files)
            response.raise_for_status()
            
        return response.json()
