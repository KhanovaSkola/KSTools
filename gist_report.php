<?php

// ...

	/**
	 * @see http://amara.readthedocs.org/en/latest/api.html#post--api2-partners-videos-[video-id]-languages-
	 */
	public function addLanguage($amara_id, $language, $title, $description, $original = FALSE)
	{
		$this->logVerbose("creating $language on video $amara_id");
		$context = stream_context_create([
			'http' => [
				'method' => 'POST',
				'header'=> implode("\r\n", [
					"X-api-username: {$this->config['username']}",
					"X-apikey: {$this->config['key']}",
					'Content-Type: application/x-www-form-urlencoded',
				]),
				'content' => http_build_query([
					'language_code' => $amara_id,
					'title' => $title,
					'description' => $description,
					'is_original' => $original ? 'true' : 'false',
				]),
			]
		]);
		$url = "http://www.amara.org/api2/partners/videos/$amara_id/languages";
		$res = file_get_contents($url, NULL, $context);
		// $data = json_decode($res);
		// if data contains node with language_code=en, success
	}
	/**
	 * @see http://amara.readthedocs.org/en/latest/api.html#post--api2-partners-videos-[video-id]-languages-[lang-identifier]-subtitles-
	 */
	public function addRevision($original_id, $amara_id, $language, $title, $description, $subs)
	{
		$this->logVerbose("creating new revision on $language video $amara_id");
		$file = __DIR__ . '/subs.temp.srt';
		file_put_contents($file, $subs);
		// $cookie = 'testcookie; testcookie; optimizelyEndUserId=oeu1393592527751r0.299231365788728; unisub-user-uuid=c9c2f97d151f40e0ab85076badbb365a6e02ece6; hide_new_messages=1166077; hide_accouncement=04/04/2014%2013%3A44%3A25; sessionid=9733cd5d432ee8d4c1f3a26a1cb5eed3; hide-yt-prompt=yes; optimizelySegments=%7B%7D; optimizelyBuckets=%7B%7D; __utma=230007235.436089838.1396713213.1396713213.1396713213.1; __utmb=230007235.1.10.1396713213; __utmc=230007235; __utmz=230007235.1396713213.1.1.utmcsr=(direct)|utmccn=(direct)|utmcmd=(none); csrftoken=rzZ4P6ozIWtbb6Fy2YQR95MbcwK0tSy0; response_time=169.750928879';
		$cookie = 'unisub-user-uuid=c9c2f97d151f40e0ab85076badbb365a6e02ece6; sessionid=9733cd5d432ee8d4c1f3a26a1cb5eed3; csrftoken=rzZ4P6ozIWtbb6Fy2YQR95MbcwK0tSy0';
		$c = curl_init();
		// $this->logVerbose('curl init for ' . 'http://www.amara.org/en/videos/' . $amara_id);
		curl_setopt($c, CURLOPT_URL, 'http://www.amara.org/en/videos/' . $amara_id);
		curl_setopt($c, CURLOPT_COOKIE, $cookie);
		curl_setopt($c, CURLOPT_FOLLOWLOCATION, TRUE);
		curl_setopt($c, CURLOPT_RETURNTRANSFER, TRUE);
		// curl_setopt($c, CURLOPT_SSL_VERIFYPEER, FALSE);
		// curl_setopt($c, CURLOPT_BUFFERSIZE, 1e7);
		// curl_setopt($c, CURLOPT_CONNECTTIMEOUT, 60);
		// curl_setopt($c, CURLOPT_DNS_CACHE_TIMEOUT, 3600);
		// curl_setopt($c, CURLOPT_LOW_SPEED_LIMIT, 1);
		// curl_setopt($c, CURLOPT_LOW_SPEED_TIME, 1000);
		curl_setopt($c, CURLOPT_TIMEOUT, 180);
		curl_setopt($c, CURLOPT_USERAGENT, 'report.khanovaskola.cz contact: mikulas@khanovaskola.cz');
		$res = curl_exec($c);
		curl_close($c);
		$match = [];
		$assert = preg_match('~id="upload-subtitles-form".*?value=\'([^\']+)\'~s', $res, $match);
		$token = $match[1];
		$assert &= preg_match('~<input type="hidden" name="video" value="(\d+)"~s', $res, $match);
		$video_id = $match[1];
		$this->logVerbose("fetched token=$token, video=$video_id");
		// $res = $this->get('http://www.amara.org/en/videos/' . $amara_id);
		// file_put_contents(__DIR__ . '/test.html', $res);
		// $match = [];
		// $assert = preg_match('~<input type="hidden" name="video" value="(\d+)"~s', $res, $match);
		// $video_id = $match[1];
		// $token = 'rzZ4P6ozIWtbb6Fy2YQR95MbcwK0tSy0';
		if (!$assert)
		{
			$this->log('not matched');
			die;
		}
		$c = curl_init();
		curl_setopt($c, CURLOPT_URL, 'http://www.amara.org/en/videos/upload_subtitles/');
		curl_setopt($c, CURLOPT_POST, TRUE);
		curl_setopt($c, CURLOPT_COOKIE, $cookie);
		curl_setopt($c, CURLOPT_FOLLOWLOCATION, TRUE);
		curl_setopt($c, CURLOPT_RETURNTRANSFER, TRUE);
		curl_setopt($c, CURLOPT_HTTPHEADER, [
			'Accept:text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
			'Accept-Language:en,en-US;q=0.8,cs;q=0.6,sk;q=0.4',
			'Cache-Control:no-cache',
			'Connection:keep-alive',
			'Pragma:no-cache',
			'Referer:http://www.amara.org/en/videos/iQpB7S8Ax6t9/info/when-is-a-particle-speeding-up/',
		]);
		curl_setopt($c, CURLOPT_USERAGENT, 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/33.0.1750.152 Safari/537.36');
		curl_setopt($c, CURLOPT_POSTFIELDS, [
			'csrfmiddlewaretoken' => $token,
			'video' => $video_id,
			'language_code' => $language,
			'primary_audio_language_code' => 'en',
			'from_language_code' => '', // empty = from video
			'complete' => 'on',
			'draft' => new CurlFile($file),
		]);
		$res = curl_exec($c);
		curl_close($c);
		if (strpos($res, 'Thank you for uploading.') === FALSE)
		{
			return $this->log("upload failed! (token='$token', video_id='$video_id', amara_id='$amara_id'");
		}
		$json = json_decode(substr($res, 10, strlen($res) - 21), TRUE);
		$this->logVerbose('http://www.amara.org' . $json['next'] . '?tab=revisions');
		
		$this->db->sync->insert([
			'original_id' => $original_id,
			'created_at' => date('Y-m-d H:i:s'),
		]);
	}