package com.campprotect.scamshield.scamdetection;

@kotlin.Metadata(mv = {1, 9, 0}, k = 1, xi = 48, d1 = {"\u0000,\n\u0002\u0018\u0002\n\u0002\u0010\u0000\n\u0002\b\u0002\n\u0002\u0010$\n\u0002\u0010\u000e\n\u0002\u0010\b\n\u0002\b\u0004\n\u0002\u0010 \n\u0002\b\u0002\n\u0002\u0018\u0002\n\u0002\b\u0004\u0018\u00002\u00020\u0001:\u0002\u0010\u0011B\u0005\u00a2\u0006\u0002\u0010\u0002J,\u0010\b\u001a\u00020\u00052\u0006\u0010\t\u001a\u00020\u00052\f\u0010\n\u001a\b\u0012\u0004\u0012\u00020\u00050\u000b2\f\u0010\f\u001a\b\u0012\u0004\u0012\u00020\u00050\u000bH\u0002J\u000e\u0010\r\u001a\u00020\u000e2\u0006\u0010\u000f\u001a\u00020\u0005R\u001a\u0010\u0003\u001a\u000e\u0012\u0004\u0012\u00020\u0005\u0012\u0004\u0012\u00020\u00060\u0004X\u0082\u0004\u00a2\u0006\u0002\n\u0000R\u001a\u0010\u0007\u001a\u000e\u0012\u0004\u0012\u00020\u0005\u0012\u0004\u0012\u00020\u00060\u0004X\u0082\u0004\u00a2\u0006\u0002\n\u0000\u00a8\u0006\u0012"}, d2 = {"Lcom/campprotect/scamshield/scamdetection/ScamDetectionEngine;", "", "()V", "keywordWeights", "", "", "", "phrasePatternWeights", "classifyContext", "text", "keywords", "", "phrases", "evaluateTranscript", "Lcom/campprotect/scamshield/scamdetection/ScamDetectionEngine$DetectionResult;", "transcript", "DetectionResult", "RiskLevel", "app_release"})
public final class ScamDetectionEngine {
    @org.jetbrains.annotations.NotNull()
    private final java.util.Map<java.lang.String, java.lang.Integer> keywordWeights = null;
    @org.jetbrains.annotations.NotNull()
    private final java.util.Map<java.lang.String, java.lang.Integer> phrasePatternWeights = null;
    
    public ScamDetectionEngine() {
        super();
    }
    
    /**
     * Conducts 4-layer hybrid evaluation of conversation transcripts
     */
    @org.jetbrains.annotations.NotNull()
    public final com.campprotect.scamshield.scamdetection.ScamDetectionEngine.DetectionResult evaluateTranscript(@org.jetbrains.annotations.NotNull()
    java.lang.String transcript) {
        return null;
    }
    
    private final java.lang.String classifyContext(java.lang.String text, java.util.List<java.lang.String> keywords, java.util.List<java.lang.String> phrases) {
        return null;
    }
    
    @kotlin.Metadata(mv = {1, 9, 0}, k = 1, xi = 48, d1 = {"\u0000,\n\u0002\u0018\u0002\n\u0002\u0010\u0000\n\u0000\n\u0002\u0010\b\n\u0000\n\u0002\u0018\u0002\n\u0000\n\u0002\u0010\u000e\n\u0000\n\u0002\u0010 \n\u0002\b\u0012\n\u0002\u0010\u000b\n\u0002\b\u0004\b\u0086\b\u0018\u00002\u00020\u0001B9\u0012\u0006\u0010\u0002\u001a\u00020\u0003\u0012\u0006\u0010\u0004\u001a\u00020\u0005\u0012\u0006\u0010\u0006\u001a\u00020\u0007\u0012\f\u0010\b\u001a\b\u0012\u0004\u0012\u00020\u00070\t\u0012\f\u0010\n\u001a\b\u0012\u0004\u0012\u00020\u00070\t\u00a2\u0006\u0002\u0010\u000bJ\t\u0010\u0015\u001a\u00020\u0003H\u00c6\u0003J\t\u0010\u0016\u001a\u00020\u0005H\u00c6\u0003J\t\u0010\u0017\u001a\u00020\u0007H\u00c6\u0003J\u000f\u0010\u0018\u001a\b\u0012\u0004\u0012\u00020\u00070\tH\u00c6\u0003J\u000f\u0010\u0019\u001a\b\u0012\u0004\u0012\u00020\u00070\tH\u00c6\u0003JG\u0010\u001a\u001a\u00020\u00002\b\b\u0002\u0010\u0002\u001a\u00020\u00032\b\b\u0002\u0010\u0004\u001a\u00020\u00052\b\b\u0002\u0010\u0006\u001a\u00020\u00072\u000e\b\u0002\u0010\b\u001a\b\u0012\u0004\u0012\u00020\u00070\t2\u000e\b\u0002\u0010\n\u001a\b\u0012\u0004\u0012\u00020\u00070\tH\u00c6\u0001J\u0013\u0010\u001b\u001a\u00020\u001c2\b\u0010\u001d\u001a\u0004\u0018\u00010\u0001H\u00d6\u0003J\t\u0010\u001e\u001a\u00020\u0003H\u00d6\u0001J\t\u0010\u001f\u001a\u00020\u0007H\u00d6\u0001R\u0011\u0010\u0006\u001a\u00020\u0007\u00a2\u0006\b\n\u0000\u001a\u0004\b\f\u0010\rR\u0011\u0010\u0002\u001a\u00020\u0003\u00a2\u0006\b\n\u0000\u001a\u0004\b\u000e\u0010\u000fR\u0017\u0010\b\u001a\b\u0012\u0004\u0012\u00020\u00070\t\u00a2\u0006\b\n\u0000\u001a\u0004\b\u0010\u0010\u0011R\u0017\u0010\n\u001a\b\u0012\u0004\u0012\u00020\u00070\t\u00a2\u0006\b\n\u0000\u001a\u0004\b\u0012\u0010\u0011R\u0011\u0010\u0004\u001a\u00020\u0005\u00a2\u0006\b\n\u0000\u001a\u0004\b\u0013\u0010\u0014\u00a8\u0006 "}, d2 = {"Lcom/campprotect/scamshield/scamdetection/ScamDetectionEngine$DetectionResult;", "", "confidenceScore", "", "riskLevel", "Lcom/campprotect/scamshield/scamdetection/ScamDetectionEngine$RiskLevel;", "category", "", "matchedKeywords", "", "matchedPhrases", "(ILcom/campprotect/scamshield/scamdetection/ScamDetectionEngine$RiskLevel;Ljava/lang/String;Ljava/util/List;Ljava/util/List;)V", "getCategory", "()Ljava/lang/String;", "getConfidenceScore", "()I", "getMatchedKeywords", "()Ljava/util/List;", "getMatchedPhrases", "getRiskLevel", "()Lcom/campprotect/scamshield/scamdetection/ScamDetectionEngine$RiskLevel;", "component1", "component2", "component3", "component4", "component5", "copy", "equals", "", "other", "hashCode", "toString", "app_release"})
    public static final class DetectionResult {
        private final int confidenceScore = 0;
        @org.jetbrains.annotations.NotNull()
        private final com.campprotect.scamshield.scamdetection.ScamDetectionEngine.RiskLevel riskLevel = null;
        @org.jetbrains.annotations.NotNull()
        private final java.lang.String category = null;
        @org.jetbrains.annotations.NotNull()
        private final java.util.List<java.lang.String> matchedKeywords = null;
        @org.jetbrains.annotations.NotNull()
        private final java.util.List<java.lang.String> matchedPhrases = null;
        
        public DetectionResult(int confidenceScore, @org.jetbrains.annotations.NotNull()
        com.campprotect.scamshield.scamdetection.ScamDetectionEngine.RiskLevel riskLevel, @org.jetbrains.annotations.NotNull()
        java.lang.String category, @org.jetbrains.annotations.NotNull()
        java.util.List<java.lang.String> matchedKeywords, @org.jetbrains.annotations.NotNull()
        java.util.List<java.lang.String> matchedPhrases) {
            super();
        }
        
        public final int getConfidenceScore() {
            return 0;
        }
        
        @org.jetbrains.annotations.NotNull()
        public final com.campprotect.scamshield.scamdetection.ScamDetectionEngine.RiskLevel getRiskLevel() {
            return null;
        }
        
        @org.jetbrains.annotations.NotNull()
        public final java.lang.String getCategory() {
            return null;
        }
        
        @org.jetbrains.annotations.NotNull()
        public final java.util.List<java.lang.String> getMatchedKeywords() {
            return null;
        }
        
        @org.jetbrains.annotations.NotNull()
        public final java.util.List<java.lang.String> getMatchedPhrases() {
            return null;
        }
        
        public final int component1() {
            return 0;
        }
        
        @org.jetbrains.annotations.NotNull()
        public final com.campprotect.scamshield.scamdetection.ScamDetectionEngine.RiskLevel component2() {
            return null;
        }
        
        @org.jetbrains.annotations.NotNull()
        public final java.lang.String component3() {
            return null;
        }
        
        @org.jetbrains.annotations.NotNull()
        public final java.util.List<java.lang.String> component4() {
            return null;
        }
        
        @org.jetbrains.annotations.NotNull()
        public final java.util.List<java.lang.String> component5() {
            return null;
        }
        
        @org.jetbrains.annotations.NotNull()
        public final com.campprotect.scamshield.scamdetection.ScamDetectionEngine.DetectionResult copy(int confidenceScore, @org.jetbrains.annotations.NotNull()
        com.campprotect.scamshield.scamdetection.ScamDetectionEngine.RiskLevel riskLevel, @org.jetbrains.annotations.NotNull()
        java.lang.String category, @org.jetbrains.annotations.NotNull()
        java.util.List<java.lang.String> matchedKeywords, @org.jetbrains.annotations.NotNull()
        java.util.List<java.lang.String> matchedPhrases) {
            return null;
        }
        
        @java.lang.Override()
        public boolean equals(@org.jetbrains.annotations.Nullable()
        java.lang.Object other) {
            return false;
        }
        
        @java.lang.Override()
        public int hashCode() {
            return 0;
        }
        
        @java.lang.Override()
        @org.jetbrains.annotations.NotNull()
        public java.lang.String toString() {
            return null;
        }
    }
    
    @kotlin.Metadata(mv = {1, 9, 0}, k = 1, xi = 48, d1 = {"\u0000\f\n\u0002\u0018\u0002\n\u0002\u0010\u0010\n\u0002\b\u0005\b\u0086\u0081\u0002\u0018\u00002\b\u0012\u0004\u0012\u00020\u00000\u0001B\u0007\b\u0002\u00a2\u0006\u0002\u0010\u0002j\u0002\b\u0003j\u0002\b\u0004j\u0002\b\u0005\u00a8\u0006\u0006"}, d2 = {"Lcom/campprotect/scamshield/scamdetection/ScamDetectionEngine$RiskLevel;", "", "(Ljava/lang/String;I)V", "LOW", "MEDIUM", "HIGH", "app_release"})
    public static enum RiskLevel {
        /*public static final*/ LOW /* = new LOW() */,
        /*public static final*/ MEDIUM /* = new MEDIUM() */,
        /*public static final*/ HIGH /* = new HIGH() */;
        
        RiskLevel() {
        }
        
        @org.jetbrains.annotations.NotNull()
        public static kotlin.enums.EnumEntries<com.campprotect.scamshield.scamdetection.ScamDetectionEngine.RiskLevel> getEntries() {
            return null;
        }
    }
}