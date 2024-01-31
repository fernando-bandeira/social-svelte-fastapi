import axios from 'axios';
import { userContext } from '../stores/userContext';

const apiBase = import.meta.env.VITE_API_PATH;

export const verifyAuth = async () => {
  try {
    const accessToken = localStorage.getItem('access');
    const res = await axios.post(apiBase + 'validate/', {
      token: accessToken
    });
    if (res.status === 200) {
      console.log('Access token válido');
      userContext.set({
        id: res.data.user_id,
        email: res.data.user_email,
      });
      return true;
    }
  } catch (error) {
    console.log('Access token inválido, tentar refresh');
    const refreshToken = localStorage.getItem('refresh');
    try {
      const refreshRes = await axios.post(apiBase + 'refresh/', {
        token: refreshToken
      });
      if (refreshRes.status === 200) {
        console.log('Refresh token válido');
        localStorage.setItem('access', refreshRes.data.access);
        localStorage.setItem('refresh', refreshRes.data.refresh);
        userContext.set({
          id: refreshRes.data.user_id,
          email: refreshRes.data.user_email,
        });
        return true;
      }
    } catch (refreshError) {
      console.log('Refresh token inválido');
      return false;
    }
  }
};
