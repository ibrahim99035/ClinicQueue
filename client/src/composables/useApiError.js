export function normalizeApiError(error) {
  let data = null;

  if (error.response) {
    data = error.response.data;
  }

  if (!data) {
    return error.message || "Something went wrong. Please try again.";
  }

  // Check for specific error fields (order matters)
  const errorFields = [
    "error",
    "warning",
    "detail",
    "message",
    "non_field_errors",
    "doctor",
    "start_date",
    "end_date",
    "email",
    "password",
    "first_name",
    "last_name",
    "phone",
    "role",
  ];

  for (const field of errorFields) {
    if (data[field]) {
      const value = data[field];
      return Array.isArray(value) ? value[0] : value;
    }
  }

  return "Please check the form data.";
}
