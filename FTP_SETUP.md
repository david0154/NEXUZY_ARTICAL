# FTP Image Upload Setup Guide

This guide explains how to configure FTP image uploading for article images.

## Quick Setup

### 1. Create FTP Configuration File

Create a file named `ftp_config.json` in the root directory of the project:

```json
{
  "ftp_host": "ftp.yourdomain.com",
  "ftp_user": "your_ftp_username",
  "ftp_pass": "your_ftp_password",
  "ftp_remote_dir": "/public_html/articles/images",
  "ftp_base_url": "https://yourdomain.com/articles/images"
}
```

### 2. Configure Your Values

Replace the following values with your actual FTP credentials:

- **ftp_host**: Your FTP server hostname (e.g., `ftp.example.com` or `192.168.1.100`)
- **ftp_user**: Your FTP username
- **ftp_pass**: Your FTP password
- **ftp_remote_dir**: The remote directory path where images will be uploaded
- **ftp_base_url**: The public URL base path for accessing uploaded images

### 3. Example Configuration

```json
{
  "ftp_host": "ftp.nexuzy.com",
  "ftp_user": "nexuzy_uploader",
  "ftp_pass": "SecurePassword123!",
  "ftp_remote_dir": "/public_html/articles/images",
  "ftp_base_url": "https://nexuzy.com/articles/images"
}
```

## Security Notes

⚠️ **IMPORTANT**: 
- The `ftp_config.json` file is already added to `.gitignore`
- **NEVER** commit this file to GitHub
- Keep your FTP credentials secure and private
- Use strong passwords for your FTP account

## How It Works

1. When you create or edit an article and select an image:
   - The image is uploaded to your FTP server
   - A unique filename is generated (e.g., `article_20260121_143045_abc123.jpg`)
   - The public URL is generated and stored in the database
   - The URL is synced to Firebase

2. When viewing article details:
   - The image is loaded from the public URL
   - Displayed in the article details dialog

## Troubleshooting

### Images Not Uploading

1. **Check FTP credentials**: Verify your `ftp_config.json` has correct details
2. **Test FTP connection**: Try connecting to your FTP server using an FTP client (FileZilla, etc.)
3. **Check permissions**: Ensure the FTP user has write permissions to the remote directory
4. **Firewall**: Make sure FTP ports (21, 20) are not blocked

### Images Not Displaying

1. **Check URL**: Verify `ftp_base_url` matches your actual public URL
2. **Check file permissions**: Uploaded files should be readable (chmod 644)
3. **Check web server**: Ensure your web server can serve files from the images directory

### Connection Errors

```
FTP connection failed: [Errno 11001] getaddrinfo failed
```
- Check if `ftp_host` is correct
- Verify DNS resolution

```
FTP connection failed: 530 Login authentication failed
```
- Check your username and password

## Alternative: Environment Variables

You can also use environment variables instead of `ftp_config.json`:

```bash
export FTP_HOST="ftp.yourdomain.com"
export FTP_USER="your_username"
export FTP_PASS="your_password"
```

## Testing

To test your FTP configuration:

1. Open the application
2. Go to "Create Article"
3. Select an image
4. The status will show:
   - "⏳ Uploading image..." during upload
   - "✅ Image uploaded!" on success
   - Error message if upload fails

## Support

For issues or questions:
- **Developer**: Manoj Konar
- **Email**: monoj@nexuzy.in
- **GitHub**: [david0154/NEXUZY_ARTICAL](https://github.com/david0154/NEXUZY_ARTICAL)

---

**Last Updated**: January 21, 2026