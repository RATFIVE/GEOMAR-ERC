import requests





class ORCIDClient:
    """Client für ORCID API."""
    
    BASE_URL = "https://pub.orcid.org/v3.0"
    
    @staticmethod
    def get_profile(orcid_id: str) -> dict | None:
        """Holt vollständiges ORCID-Profil."""
        url = f"{ORCIDClient.BASE_URL}/{orcid_id}"
        headers = {'Accept': 'application/json'}
        
        try:
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            print(f"❌ ORCID API Fehler: {e}")
            return None
    
    @staticmethod
    def get_current_affiliation(orcid_id: str) -> str | None:
        """
        Holt die aktuelle Affiliation (neueste Employment oder Education).
        
        Returns:
            Name der Institution oder None
        """
        profile = ORCIDClient.get_profile(orcid_id)
        
        if not profile:
            return None
        
        try:
            activities = profile.get('activities-summary', {})
            

            # 1. Versuch: Employments (bevorzugt)
            employments = activities.get('employments', {})
            if employments:
                employment_groups = employments.get('affiliation-group', [])
                
                # Alle Employments mit End-Datum = None (aktuell) oder neuestes Jahr
                current_employments = []
                
                for group in employment_groups:
                    summaries = group.get('summaries', [])
                    for summary in summaries:
                        employment_summary = summary.get('employment-summary', {})
                        
                        # Prüfe ob aktuell (kein End-Datum)
                        end_date = employment_summary.get('end-date')
                        
                        if end_date is None:  # Aktuell
                            org_name = employment_summary.get('organization', {}).get('name')
                            if org_name:
                                return org_name
                        
                        # Sammle alle mit Datum für Fallback
                        start_date = employment_summary.get('start-date', {})
                        year = start_date.get('year', {}).get('value', 0) if start_date else 0
                        
                        current_employments.append({
                            'name': employment_summary.get('organization', {}).get('name'),
                            'year': year,
                            'end_date': end_date
                        })
                
                # Wenn kein aktuelles gefunden: Nimm das neueste
                if current_employments:
                    latest = max(current_employments, key=lambda x: x['year'])
                    return latest['name']
            
            # # 2. Versuch: Education (falls keine Employment)
            # educations = activities.get('educations', {})
            # if educations:
            #     education_groups = educations.get('affiliation-group', [])
                
            #     for group in education_groups:
            #         summaries = group.get('summaries', [])
            #         for summary in summaries:
            #             education_summary = summary.get('education-summary', {})
                        
            #             end_date = education_summary.get('end-date')
            #             if end_date is None:  # Noch in Ausbildung
            #                 org_name = education_summary.get('organization', {}).get('name')
            #                 if org_name:
            #                     return org_name
            
            # # 3. Fallback: Erste gefundene Institution
            # if employment_groups:
            #     first_group = employment_groups[0]
            #     summaries = first_group.get('summaries', [])
            #     if summaries:
            #         first_summary = summaries[0].get('employment-summary', {})
            #         org = first_summary.get('organization', {})
            #         return org.get('name')
        
        except (KeyError, ValueError, TypeError) as e:
            print(f"⚠️ Fehler beim Extrahieren der Affiliation: {e}")
        
        return None
    
    @staticmethod
    def get_keywords(orcid_id: str) -> list[str]:
        """Holt nur Keywords."""
        url = f"{ORCIDClient.BASE_URL}/{orcid_id}/keywords"
        headers = {'Accept': 'application/json'}
        
        try:
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            keywords_list = data.get('keyword', [])
            return [
                kw.get('content') 
                for kw in keywords_list 
                if kw.get('content')
            ]
        except:
            return []
    
    @staticmethod
    def get_biography(orcid_id: str) -> str | None:
        """Holt nur Biografie."""
        profile = ORCIDClient.get_profile(orcid_id)
        
        if not profile:
            return None
        
        try:
            person = profile.get('person', {})
            biography_obj = person.get('biography')
            
            if biography_obj and isinstance(biography_obj, dict):
                return biography_obj.get('content')
        except:
            pass
        
        return None
    
    @staticmethod
    def get_research_info(orcid_id: str) -> dict:
        """
        Kombiniert alle relevanten Forschungsinformationen inkl. Affiliation.
        
        Returns:
            Dictionary mit affiliation, biography, keywords, works_count
        """
        profile = ORCIDClient.get_profile(orcid_id)
        
        if not profile:
            return {
                'affiliation': None,
                'biography': None,
                'keywords': [],
                'works_count': 0,
                'orcid': orcid_id
            }
        
        # Aktuelle Affiliation
        affiliation = ORCIDClient.get_current_affiliation(orcid_id)
        
        # Biografie
        biography = None
        person = profile.get('person', {})
        bio_obj = person.get('biography')
        if bio_obj and isinstance(bio_obj, dict):
            biography = bio_obj.get('content')
        
        # Keywords
        keywords = []
        kw_obj = person.get('keywords', {})
        if kw_obj and isinstance(kw_obj, dict):
            kw_list = kw_obj.get('keyword', [])
            keywords = [
                kw.get('content') 
                for kw in kw_list 
                if isinstance(kw, dict) and kw.get('content')
            ]
        
        # Publikationsanzahl
        works_count = 0
        activities = profile.get('activities-summary', {})
        if activities:
            works = activities.get('works', {})
            if works and isinstance(works, dict):
                works_group = works.get('group', [])
                works_count = len(works_group) if isinstance(works_group, list) else 0
        
        return {
            'affiliation': affiliation,
            'biography': biography,
            'keywords': keywords,
            'works_count': works_count,
            'orcid': orcid_id
        }