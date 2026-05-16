// config.js
// 🔑 ဒီမှာ သင့် GitHub Username, Repo, Token ထည့်ပါ

const CONFIG = {
    // သင့် GitHub Username
    GITHUB_USER: "yinthuaung15",
    
    // data.json ထည့်ထားတဲ့ Repository Name
    GITHUB_REPO: "motorcycle-data",
    
    // GitHub Personal Access Token (ghp_ နဲ့စရမယ်)
    GITHUB_TOKEN: "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",
    
    // API URL (အလိုလျောက်ဖြစ်မယ် - ပြင်စရာမလိုပါ)
    get API_URL() {
        return "https://api.github.com/repos/" + this.GITHUB_USER + "/" + this.GITHUB_REPO + "/contents/data.json";
    }
};
