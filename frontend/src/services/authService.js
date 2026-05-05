// import apiClient from './apiClient';

// export const authService = {
//   login: (email, password) =>
//     apiClient.post('/auth/login', new URLSearchParams({ username: email, password }), {
//       headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
//     }),

//   register: (data) => apiClient.post('/auth/register', data),

//   logout: (token) =>
//     apiClient.post('/auth/logout', null, {
//       headers: { Authorization: `Bearer ${token}` },
//     }),

//   refreshToken: (refreshToken) =>
//     apiClient.post('/auth/refresh', null, {
//       params: { refresh_token: refreshToken },
//     }),

//   getMe: (token) =>
//     apiClient.get('/users/me', {
//       headers: { Authorization: `Bearer ${token}` },
//     }),

//   forgotPassword: (email) =>
//     apiClient.post('/auth/forgot-password', { email }),

//   resetPassword: (token, password) =>
//     apiClient.post('/auth/reset-password', {
//       token,
//       new_password: password
//     }),
// };


import apiClient from './apiClient';

export const authService = {
  // LOGIN (FIXED: JSON)
  login: (email, password) =>
    apiClient.post('/auth/login', {
      email,
      password
    }),

  // REGISTER
  register: (data) =>
    apiClient.post('/auth/register', data),

  // LOGOUT
  logout: (token) =>
    apiClient.post('/auth/logout', null, {
      headers: {
        Authorization: `Bearer ${token}`
      }
    }),


  // REFRESH TOKEN (FIXED: JSON BODY)
  refreshToken: (refreshToken) =>
    apiClient.post('/auth/refresh', {
      refresh_token: refreshToken
    }),


  // GET CURRENT USER

  getMe: (token) =>
    apiClient.get('/users/me', {
      headers: {
        Authorization: `Bearer ${token}`
      }
    }),

 
  // FORGOT PASSWORD (FIXED: JSON)

  forgotPassword: (email) =>
    apiClient.post('/auth/forgot-password', {
      email
    }),

  // RESET PASSWORD
  resetPassword: (token, password) =>
    apiClient.post('/auth/reset-password', {
      token,
      new_password: password
    }),
};
