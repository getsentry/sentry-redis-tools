# Silo Boundary Violation Fix

## Problem
REGION silo service directly accessing CONTROL-plane Integration model causing 400 Bad Request.

## Root Cause  
DatabaseBackedIntegrationService.get_integration uses Integration.objects.get() directly from REGION mode.

## Solution
Use hybrid cloud integration service instead of direct model access.

## Fix Location
File: src/sentry/integrations/services/integration/impl.py
Method: DatabaseBackedIntegrationService.get_integration

## Code Change
Replace direct Integration model access with hybrid cloud service call.

## Result
- Eliminates SiloLimit.AvailabilityError
- Fixes 400 Bad Request in get_github_enterprise_integration_config  
- Allows GitHub Enterprise repos to initialize properly in Autofix
