# Design Decisions

## ESF-Aligned Philosophy

This accelerator deliberately chooses **speed-to-value over completeness**. Every decision prioritizes rapid demonstration of capabilities while maintaining production-ready patterns.

## Key Decisions

### 1. Hugging Face Free Tier over OpenAI

**Decision**: Use Hugging Face Inference API instead of OpenAI.

**Rationale**:
- Zero cost for demonstration and testing
- No credit card required for initial setup
- Sufficient quality for accelerator purposes
- Easy to swap to production LLM later

**Trade-offs**:
- Slower inference than OpenAI GPT-4
- Less consistent output quality
- Rate limits on free tier

---

### 2. PostgreSQL with SQLAlchemy Async

**Decision**: Use PostgreSQL as the persistence layer with async SQLAlchemy.

**Rationale**:
- Industry-standard relational database
- Demonstrates enterprise data modeling skills
- Native JSON column support for flexible storage
- Async driver for non-blocking I/O

**Trade-offs**:
- Requires running PostgreSQL (Docker simplifies this)
- More setup than SQLite for local development

---

### 3. FAISS over Chroma for RAG

**Decision**: Use FAISS for vector storage instead of Chroma.

**Rationale**:
- No external service dependency
- Faster for small-scale demonstrations
- Well-documented and widely used
- In-memory mode suitable for accelerator

**Trade-offs**:
- No persistence between restarts (acceptable for demo)
- Less feature-rich than Chroma

---

### 4. Heuristic Confidence vs. True ML Confidence

**Decision**: Display heuristic-based "confidence" scores with clear disclaimers.

**Rationale**:
- True confidence requires calibrated models
- Heuristics provide useful UX signal
- Explicit labeling prevents misinterpretation
- Demonstrates awareness of AI limitations

**Trade-offs**:
- Not a true probability measure
- Users must understand the disclaimer

---

### 5. Light Theme Only

**Decision**: Implement only a light color scheme.

**Rationale**:
- Aligns with CACI brand guidelines
- Simpler CSS maintenance
- Ensures accessibility focus on one theme
- Reduces decision complexity

**Trade-offs**:
- No dark mode for user preference
- May not suit all environments

---

### 6. Prompt Templates in Files

**Decision**: Store LLM prompts in `/prompts/*.txt` files.

**Rationale**:
- Easy to review and modify
- Version-controllable separately
- Non-developers can review prompts
- Promotes prompt engineering practices

**Trade-offs**:
- Requires file system access
- Less dynamic than database storage

---

### 7. No Authentication

**Decision**: Deliberately exclude authentication/authorization.

**Rationale**:
- Explicitly out of scope per requirements
- Reduces complexity for demonstration
- Allows focus on core AI capabilities
- Would be added in production version

**Trade-offs**:
- Not suitable for multi-user deployment
- No audit trail per user

---

## What This Accelerator Is NOT

1. **Not production-ready**: Missing security, auth, and hardening
2. **Not a complete solution**: Delivers 60-75% value intentionally
3. **Not optimized**: Favors clarity over performance
4. **Not enterprise-scale**: Designed for demonstration workloads

## Future Enhancement Paths

| Enhancement | Effort | Value |
|-------------|--------|-------|
| Add Azure AD auth | Medium | High |
| Use Azure OpenAI | Low | Medium |
| Add batch processing | Medium | Medium |
| Implement caching | Low | Medium |
| Add export features | Low | High |
