# PaLaDiN DSL Semantics

## Operators

### Basic Logical Operators
- And
- Or
- Not

## Basic Temporal Operators
- Finally
- Globally
- Next
- Until
- Release

### New Temporal Operators

- Before: A Happened Before B
   ```
      B(ϕ, ψ) := ∃i, ∃k, 0 <= k <= i, ω_i ⊨ ψ ==> ω_k ⊨ ϕ
      Also:
      B(ϕ, ψ) == U(¬G(¬ϕ), ψ)
  ```
- After: A Happened After B
  ```
    A(ϕ, ψ) == B(ψ, ϕ)
  ```
  
- All Future: From now on, A always happen.
  ```
    ₣(ϕ) := G(X(ϕ))
  ```