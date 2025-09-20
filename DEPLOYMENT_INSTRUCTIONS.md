# 🚀 Deployment Instructions - FastAPI ML Recommendations API

Your API is ready for deployment! Choose your preferred platform below.

## ✅ **Pre-Deployment Checklist**

- ✅ Git repository initialized
- ✅ All files committed
- ✅ `app/` folder with modular structure
- ✅ `requirements.txt` with dependencies
- ✅ `Procfile` configured for cloud deployment
- ✅ `README.md` with documentation

## 🌐 **Deployment Options**

### **Option 1: Railway (Recommended) 🚂**

Railway is the easiest for FastAPI deployment with automatic builds.

#### **Steps:**

1. **Push to GitHub:**
   ```bash
   # Create GitHub repository first, then:
   git remote add origin https://github.com/yourusername/your-repo.git
   git branch -M main
   git push -u origin main
   ```

2. **Deploy on Railway:**
   - Go to [railway.app](https://railway.app)
   - Click "Deploy from GitHub repo"
   - Connect your GitHub account
   - Select your repository
   - Railway auto-detects FastAPI and deploys!

3. **Configuration:**
   - Build Command: `pip install -r requirements.txt` (auto-detected)
   - Start Command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT` (from Procfile)

#### **Expected Result:**
- Your API will be available at: `https://your-app-name.railway.app`
- Health check: `https://your-app-name.railway.app/health`
- Docs: `https://your-app-name.railway.app/docs`

---

### **Option 2: Render 🎨**

Great for free deployments with good performance.

#### **Steps:**

1. **Push to GitHub** (same as above)

2. **Deploy on Render:**
   - Go to [render.com](https://render.com)
   - Click "New Web Service"
   - Connect your GitHub repository
   - Configure:
     - **Build Command**: `pip install -r requirements.txt`
     - **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
     - **Python Version**: 3.11

3. **Deploy**: Click "Create Web Service"

#### **Expected Result:**
- Your API will be available at: `https://your-app-name.onrender.com`

---

### **Option 3: Vercel ⚡**

Serverless deployment, great for APIs with variable traffic.

#### **Steps:**

1. **Install Vercel CLI:**
   ```bash
   npm install -g vercel
   ```

2. **Create vercel.json:**
   ```json
   {
     "builds": [
       {
         "src": "app/main.py",
         "use": "@vercel/python"
       }
     ],
     "routes": [
       {
         "src": "/(.*)",
         "dest": "app/main.py"
       }
     ]
   }
   ```

3. **Deploy:**
   ```bash
   vercel --prod
   ```

#### **Expected Result:**
- Your API will be available at: `https://your-app-name.vercel.app`

---

## 🧪 **Testing Your Deployed API**

Once deployed, test these endpoints:

### **1. Health Check**
```bash
curl https://your-app-name.railway.app/health
```
**Expected Response:**
```json
{
  "status": "ok",
  "service": "ML Recommendations API",
  "version": "1.0.0",
  "timestamp": "2024-01-15T10:30:45.123456"
}
```

### **2. Get Recommendations**
```bash
curl -X POST "https://your-app-name.railway.app/recommendations" \
     -H "Content-Type: application/json" \
     -d '{
       "student_id": "STU_001",
       "skills": ["Python", "Machine Learning", "SQL"],
       "stream": "Computer Science",
       "cgpa": 8.5,
       "rural_urban": "Urban",
       "college_tier": "Tier-1"
     }'
```

### **3. API Documentation**
Visit: `https://your-app-name.railway.app/docs`

## 🔧 **Environment Variables (Optional)**

For production, you can set these environment variables:

- `ENVIRONMENT`: `production`
- `LOG_LEVEL`: `info`
- `DATA_PATH`: Path to CSV files (if using external storage)

## 🚨 **Common Issues & Solutions**

### **Issue: Module Import Error**
**Solution**: Ensure `Procfile` uses `app.main:app` (not `main:app`)

### **Issue: Port Binding Error**
**Solution**: Make sure your app uses `$PORT` environment variable

### **Issue: Dependencies Not Found**
**Solution**: Verify all dependencies are in `requirements.txt`

### **Issue: 404 on Endpoints**
**Solution**: Check that routes are defined correctly in `app/main.py`

## 📊 **Monitoring Your Deployment**

### **Railway:**
- View logs in Railway dashboard
- Monitor resource usage
- Set up custom domains

### **Render:**
- Check build and deploy logs
- Monitor service health
- Configure environment variables

### **Vercel:**
- View function logs
- Monitor performance metrics
- Set up custom domains

## 🎯 **Next Steps After Deployment**

1. **Test all endpoints** thoroughly
2. **Set up monitoring** and alerts
3. **Configure custom domain** (optional)
4. **Set up CI/CD** for automatic deployments
5. **Replace mock ML model** with actual implementation
6. **Add authentication** if needed
7. **Scale resources** based on usage

## 🚀 **Quick Deploy Commands**

### **For Railway:**
```bash
# After creating GitHub repo
git remote add origin https://github.com/yourusername/your-repo.git
git push -u origin main
# Then connect repo in Railway dashboard
```

### **For Render:**
```bash
# Same as Railway - push to GitHub, then connect in Render
git push origin main
```

### **For Vercel:**
```bash
# Install Vercel CLI and deploy directly
npm install -g vercel
vercel --prod
```

---

**Your FastAPI ML Recommendations API is ready for production! 🎉**

Choose your platform and deploy now! 🚀
