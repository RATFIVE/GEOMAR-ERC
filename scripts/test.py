"""
Field of Study Analyzer für Semantic Scholar

Installation:
pip install semanticscholar matplotlib pandas

Erstellt umfassende Übersichten über Forschungsfelder eines Wissenschaftlers
"""

from semanticscholar import SemanticScholar
from collections import Counter, defaultdict
import json

class FieldOfStudyAnalyzer:
    def __init__(self, api_key=None):
        self.sch = SemanticScholar(api_key=api_key)
    
    def get_fields_overview(self, author_id, max_papers=200):
        """
        Erstellt eine umfassende Übersicht über alle Fields of Study
        """
        print(f"📊 Analysiere Fields of Study für Author ID: {author_id}")
        print("=" * 80)
        
        # Autor und Papers laden
        author = self.sch.get_author(author_id)
        
        if not author:
            print("❌ Autor nicht gefunden")
            return None
        
        print(f"\n👤 Autor: {author.name}")
        print(f"📚 Analysiere {min(len(author.papers) if author.papers else 0, max_papers)} Papers...\n")
        
        # Datenstrukturen für Analyse
        all_fields = []
        field_by_year = defaultdict(lambda: defaultdict(int))
        field_citations = defaultdict(int)
        field_papers = defaultdict(list)
        papers_with_fields = 0
        
        papers = author.papers[:max_papers] if author.papers else []
        
        for paper in papers:
            # Fields of Study sammeln
            if hasattr(paper, 'fieldsOfStudy') and paper.fieldsOfStudy:
                papers_with_fields += 1
                for field in paper.fieldsOfStudy:
                    all_fields.append(field)
                    
                    # Nach Jahr gruppieren
                    if paper.year:
                        field_by_year[field][paper.year] += 1
                    
                    # Zitationen pro Field
                    if paper.citationCount:
                        field_citations[field] += paper.citationCount
                    
                    # Papers pro Field speichern
                    field_papers[field].append({
                        'title': paper.title,
                        'year': paper.year,
                        'citations': paper.citationCount
                    })
        
        # Analyse durchführen
        field_counts = Counter(all_fields)
        total_papers = len(papers)
        
        print(f"✅ {papers_with_fields} von {total_papers} Papers haben Field-Informationen\n")
        
        return {
            'author': author,
            'field_counts': field_counts,
            'field_by_year': field_by_year,
            'field_citations': field_citations,
            'field_papers': field_papers,
            'total_papers': total_papers,
            'papers_with_fields': papers_with_fields
        }
    
    def print_summary(self, analysis):
        """Druckt eine übersichtliche Zusammenfassung"""
        if not analysis:
            return
        
        field_counts = analysis['field_counts']
        field_citations = analysis['field_citations']
        total_papers = analysis['total_papers']
        
        print("\n" + "=" * 80)
        print("📊 FIELDS OF STUDY - ÜBERSICHT")
        print("=" * 80)
        
        print(f"\n{'Rang':<5} {'Field of Study':<35} {'Papers':<10} {'%':<8} {'Zitate':<10}")
        print("-" * 80)
        
        for i, (field, count) in enumerate(field_counts.most_common(20), 1):
            percentage = (count / total_papers) * 100
            citations = field_citations.get(field, 0)
            print(f"{i:<5} {field:<35} {count:<10} {percentage:>6.1f}% {citations:>10,}")
        
        print("\n" + "=" * 80)
    
    def print_detailed_breakdown(self, analysis, top_n=10):
        """Detaillierte Aufschlüsselung der Top-Fields"""
        if not analysis:
            return
        
        field_counts = analysis['field_counts']
        field_papers = analysis['field_papers']
        
        print("\n" + "=" * 80)
        print(f"🔍 DETAILLIERTE ANALYSE - TOP {top_n} FIELDS")
        print("=" * 80)
        
        for i, (field, count) in enumerate(field_counts.most_common(top_n), 1):
            papers = field_papers[field]
            
            # Top 3 meistzitierte Papers in diesem Field
            top_papers = sorted(papers, 
                              key=lambda x: x['citations'] if x['citations'] else 0, 
                              reverse=True)[:3]
            
            print(f"\n{i}. 🏷️  {field.upper()}")
            print(f"   📄 Anzahl Papers: {count}")
            print(f"   📈 Top Papers:")
            
            for j, paper in enumerate(top_papers, 1):
                citations = paper['citations'] if paper['citations'] else 0
                year = paper['year'] if paper['year'] else 'N/A'
                print(f"      {j}. {paper['title'][:70]}...")
                print(f"         Jahr: {year} | Zitationen: {citations:,}")
        
        print("\n" + "=" * 80)
    
    def analyze_field_evolution(self, analysis, top_fields=5):
        """Zeigt die Entwicklung der Fields über die Zeit"""
        if not analysis:
            return
        
        field_counts = analysis['field_counts']
        field_by_year = analysis['field_by_year']
        
        print("\n" + "=" * 80)
        print(f"📈 ENTWICKLUNG DER TOP {top_fields} FIELDS ÜBER DIE ZEIT")
        print("=" * 80)
        
        for field, _ in field_counts.most_common(top_fields):
            print(f"\n🏷️  {field}:")
            
            years_data = field_by_year[field]
            if years_data:
                sorted_years = sorted(years_data.items())
                
                # Timeline ausgeben
                print("   ", end="")
                for year, count in sorted_years[-10:]:  # Letzte 10 Jahre
                    print(f"{year}: {count} | ", end="")
                print()
                
                # Trend berechnen
                recent_years = [count for year, count in sorted_years[-3:]]
                older_years = [count for year, count in sorted_years[-6:-3]] if len(sorted_years) > 3 else []
                
                if older_years and recent_years:
                    avg_recent = sum(recent_years) / len(recent_years)
                    avg_older = sum(older_years) / len(older_years)
                    
                    if avg_recent > avg_older * 1.2:
                        trend = "📈 Steigend"
                    elif avg_recent < avg_older * 0.8:
                        trend = "📉 Abnehmend"
                    else:
                        trend = "➡️  Stabil"
                    
                    print(f"   Trend: {trend}")
        
        print("\n" + "=" * 80)
    
    def export_to_json(self, analysis, filename):
        """Exportiert die Analyse als JSON"""
        if not analysis:
            return
        
        # JSON-serialisierbare Version erstellen
        export_data = {
            'author': {
                'name': analysis['author'].name,
                'authorId': analysis['author'].authorId,
                'paperCount': analysis['author'].paperCount,
                'citationCount': analysis['author'].citationCount,
                'hIndex': analysis['author'].hIndex
            },
            'fields_summary': [
                {
                    'field': field,
                    'paper_count': count,
                    'percentage': (count / analysis['total_papers']) * 100,
                    'total_citations': analysis['field_citations'].get(field, 0)
                }
                for field, count in analysis['field_counts'].most_common()
            ],
            'statistics': {
                'total_papers': analysis['total_papers'],
                'papers_with_fields': analysis['papers_with_fields'],
                'unique_fields': len(analysis['field_counts'])
            }
        }
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, indent=2, ensure_ascii=False)
        
        print(f"\n💾 Daten exportiert nach: {filename}")
    
    def get_field_combinations(self, analysis, min_count=3):
        """Findet häufige Kombinationen von Fields (Interdisziplinarität)"""
        if not analysis:
            return
        
        print("\n" + "=" * 80)
        print("🔗 HÄUFIGE FIELD-KOMBINATIONEN (Interdisziplinarität)")
        print("=" * 80)
        
        field_papers = analysis['field_papers']
        
        # Papers durchgehen und Field-Kombinationen finden
        combinations = Counter()
        
        for field1 in field_papers:
            for field2 in field_papers:
                if field1 < field2:  # Duplikate vermeiden
                    # Gemeinsame Papers finden
                    papers1 = {p['title'] for p in field_papers[field1]}
                    papers2 = {p['title'] for p in field_papers[field2]}
                    common = len(papers1 & papers2)
                    
                    if common >= min_count:
                        combinations[(field1, field2)] = common
        
        print(f"\nTop 10 Field-Kombinationen (min. {min_count} gemeinsame Papers):\n")
        for i, ((field1, field2), count) in enumerate(combinations.most_common(10), 1):
            print(f"{i:2}. {field1} ↔ {field2}")
            print(f"    Gemeinsame Papers: {count}")
        
        print("\n" + "=" * 80)


# Hauptprogramm
if __name__ == "__main__":
    # Analyzer initialisieren
    analyzer = FieldOfStudyAnalyzer()
    
    # Beispiel: Analysiere einen Autor
    # Ersetze mit echter Author ID oder suche zuerst nach Namen
    
    print("🔍 FIELD OF STUDY ANALYZER")
    print("=" * 80)
    print("\nBeispiel 1: Suche nach Autor\n")
    
    # Nach Autor suchen
    search_name = "Frank Witlox"  # Beispielname - ersetzen
    authors = analyzer.sch.search_author(search_name, limit=3)
    
    if authors:
        print(f"Gefundene Autoren für '{search_name}':\n")
        for i, author in enumerate(authors, 1):
            print(f"{i}. {author.name} (ID: {author.authorId})")
            print(f"   Papers: {author.paperCount}, Citations: {author.citationCount}")
        
        # Ersten Autor analysieren
        author_id = authors[0].authorId
        print(f"\n📊 Analysiere: {authors[0].name}")
        print("=" * 80)
        
        # Vollständige Analyse durchführen
        analysis = analyzer.get_fields_overview(author_id, max_papers=200)
        
        if analysis:
            # Verschiedene Übersichten ausgeben
            analyzer.print_summary(analysis)
            analyzer.print_detailed_breakdown(analysis, top_n=5)
            analyzer.analyze_field_evolution(analysis, top_fields=5)
            analyzer.get_field_combinations(analysis, min_count=3)
            
            # Optional: Export
            # analyzer.export_to_json(analysis, 'field_analysis.json')
    else:
        print(f"❌ Keine Autoren gefunden für: {search_name}")