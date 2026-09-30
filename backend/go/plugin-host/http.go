package pluginhost

import (
	"im-platform/backend/go/shared"
	"net/http"
)

// No plugin business is introduced in this Auth remediation.
func NewHandler() http.Handler { return shared.InfraMux("plugin-host") }
