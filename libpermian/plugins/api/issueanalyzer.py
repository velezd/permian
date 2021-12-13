from ...issueanalyzer.proxy import IssueAnalyzerProxy

def register(AnalyzerClass):
    return IssueAnalyzerProxy.register(AnalyzerClass)
