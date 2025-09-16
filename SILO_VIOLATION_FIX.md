# Fix for Silo Boundary Violation in GitHub Enterprise Integration Config

## Issue Summary
The error occurs because a REGION silo service is attempting to directly access a CONTROL-plane Integration model, violating Sentry's silo architecture.

## Root Cause
The `DatabaseBackedIntegrationService.get_integration` method is directly querying the `Integration` model using `Integration.objects.get()` from within a REGION silo context.

## Solution
Replace direct Integration model access with hybrid cloud service call.

## Files to Modify

### 1. src/sentry/integrations/services/integration/impl.py

In the `DatabaseBackedIntegrationService.get_integration` method:

```python
def get_integration(
    self,
    integration_id: int,
    provider: str,
    organization_id: int | None = None,
    status: int = ObjectStatus.ACTIVE,
) -> Integration | None:
    # BEFORE (causes silo violation):
    # integration = Integration.objects.get(**integration_kwargs)
    
    # AFTER (silo-aware):
    from sentry.services.hybrid_cloud.integration import integration_service
    return integration_service.get_integration(
        integration_id=integration_id,
        provider=provider,
        organization_id=organization_id,
        status=status,
    )
```

## Expected Result
- Eliminates SiloLimit.AvailabilityError
- Fixes 400 Bad Request in get_github_enterprise_integration_config  
- Allows GitHub Enterprise repos to initialize properly in Autofix
